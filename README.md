## Parte 1: Introducción a Docker

### Ejercicio N°1:
Se agregó en el archivo *docker-compose-dev* original un nuevo servicio, copia de client1 , pero reemplazando el `1` por un `2` (en el nombre y en la variable de entorno `CLI_ID`).  
Al ejecutar docker-compose-up, el sistema inicia esta vez con 2 clientes de forma satisfactoria:
```bash
server   | 2024-03-14 21:30:36 INFO     action: accept_connections | result: in_progress
server   | 2024-03-14 21:30:36 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-03-14 21:30:36 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-03-14 21:30:36 INFO     action: accept_connections | result: in_progress
server   | 2024-03-14 21:30:36 INFO     action: accept_connections | result: success | ip: 172.25.125.4
server   | 2024-03-14 21:30:36 INFO     action: receive_message | result: success | ip: 172.25.125.4 | msg: [CLIENT 2] Message N°1
client2  | time="2024-03-14 21:30:36" level=info msg="action: config | result: success | client_id: 2 | server_address: server:12345 | loop_lapse: 20s | loop_period: 5s | log_level: DEBUG"
client2  | time="2024-03-14 21:30:36" level=info msg="action: receive_message | result: success | client_id: 2 | msg: [CLIENT 2] Message N°1\n"
client1  | time="2024-03-14 21:30:36" level=info msg="action: config | result: success | client_id: 1 | server_address: server:12345 | loop_lapse: 20s | loop_period: 5s | log_level: DEBUG"
client1  | time="2024-03-14 21:30:36" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1\n"
```

### Ejercicio N°1.1:
Se agregó el archivo *n_clients_compose.py* en la carpeta raiz del proyecto, el cual sobreescribe el archivo *docker-compose-dev.yaml* con un número de clientes definido por el usuario.  
Para ejecutarlo, se debe correr el siguiente comando (reemplazando `3` por el número de clientes deseado):
```bash
python n_clients_compose.py 3
```
Luego, al ejecutar `make docker-compose-up`, el sistema inicia con la cantidad de clientes definida:
```bash
% make docker-compose-up
.
.
.
docker compose -f docker-compose-dev.yaml up -d --build
[+] Running 5/5
 ✔ Network tp0_testing_net  Created
 ✔ Container server         Started
 ✔ Container client3        Started
 ✔ Container client2        Started
 ✔ Container client1        Started     
```

### Ejercicio N°2:
Se agregan volúmenes en la definición del docker-compose (y en el script generador también) tanto en el server como en los clientes de la siguiente forma:
```yaml
# server
volumes:
      - ./server/config.ini:/config.ini


# client
volumes:
      - ./client/config.yaml:/config.yaml
```

También se puede eliminar la linea que copiaba el archivo de configuración del dockerfile del cliente, que ya no es necesaria.  
De esta manera, se puede comprobar que al hacer un cambio en cualquiera de los dos archivos, y volver a levantar el respectivo contenedor (sin necesidad de hacer un build nuevo) este se  levantará con la nueva configuración.

### Ejercicio N°3:
Se agregó un nuevo archivo `docker-compose-test.yaml` que levanta un nuevo servicio llamado `test_client` que ejecuta el script `netcat-test.sh` que envía un mensaje al servidor utilizando netcat, y verifica que el mensaje recibido sea el mismo.  
Se agregó además en el makefile la regla `docker-compose-test-up` que levanta este nuevo servicio junto con el servidor y al finalizar los detiene (se agregó `--abort-on-container-exit` en el comando de ejecución de docker compose para esto).  
El resultado exitoso (o no) del test se puede comprobar por consola:
```bash
[+] Running 2/0
 ✔ Container server       Created                                                                                                                                                                                                                                        0.0s 
 ✔ Container test_client  Created                                                                                                                                                                                                                                        0.0s 
Attaching to server, test_client
server       | 2024-03-22 03:12:37 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server       | 2024-03-22 03:12:37 INFO     action: accept_connections | result: in_progress
test_client  | Sending message to server: Hello, world!
server       | 2024-03-22 03:12:37 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server       | 2024-03-22 03:12:37 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: Hello, world!
server       | 2024-03-22 03:12:37 INFO     action: accept_connections | result: in_progress
test_client  | Received message from server: Hello, world!
test_client  | Test passed: Sent and received messages are the same.
test_client exited with code 0
Aborting on container exit...
[+] Stopping 2/2
 ✔ Container test_client  Stopped                                                                                                                                                                                                                                        0.0s 
 ✔ Container server       Stopped     
```

### Ejercicio N°4:
Se hicieron las siguientes modificaciones en código del servidor y del cliente:
 - Servidor:
      - Se agregó el atributo `should_stop`, por defecto en *False*, y el método `Server.stop()` para setearlo en *True*, y además hacer *shutdown* y *close* del `server_socket`.
      - En el método `Server.run()`, se agregó como condición del *while* que `should_stop` sea *False*.
            - Es decir que cuando `should_stop` sea *True*, el servidor dejará de aceptar conexiones y terminará.
      - Se agregó un handler (utilizando la lib *Signals*) para capturar la señal `SIGTERM`.
            - Cuando se reciba esta señal, se llamará al método `Server.stop()`.
            - De esta forma el servidor terminará de responder al cliente actual (de existir), sin aceptar nuevas conexiones, y luego terminará su ejecución.
 - Cliente:  
      - Se agregaron los channels `signals` y `shouldStop`.
           - `signals` recibe las señales del sistema y se configura para reaccionar a `SIGTERM`.
           - `shouldStop` es un `chan bool` que se setea en *True* cuando se recibe la señal `SIGTERM`.
                - Esto se hace dentro de una *goroutine* iniciada en main, para no bloquear la ejecución del programa.
      - Se agrega el atributo `shouldStop` en la estructura `Client`, donde se pasa en la construcción del cliente el channel `shouldStop`.
      - En el *case* de `StartClientLoop()` se agrega una rama que verifica si se recibe un *true* en el channel `shouldStop`.
           - Si es así, se cierra el socket y se sale del loop.  

Como por defecto el cliente ejecuta el loop cada 5 segundos, también se aumentó el tiempo para esperar antes de mandar un SIGKILL en el comando docker-compose-down, a `-t 6`, ya que puede pasar que el cliente no haya llegado a ejecutar el loop antes de que se cierre el contenedor (por defecto son 5 segundos, si eso cambiara habría que modificar de vuelta el `-t`).  

### Ejercicio N°5:
- Cliente:  
    - Se agregaron las nuevas variables de entorno en forma similar a las existentes.  
        - Pero en estas nuevas variables se hace un saneamiendo previo, eliminando los caracteres `|` y `\n` de los valores.
    - Se agregaron 3 nuevos clientes en el docker compose, y ahora todos tienen todas las nuevas variables de entorno de las apuestas a realizar.
    - Se agregó el archivo `common/protocol.go` con las funciones para enviar y recibir mensajes de apuestas hacia y desde el servidor, con el formato:  
        ```go
            ID|NOMBRE|APELLIDO|DOCUMENTO|NACIMIENTO|NUMERO\n
        ```
    - Se modificó el archivo `client/client.go` para que ahora se utilice el protocolo para enviar y recibir mensajes. Se agregaron además los logs pedidos.
    - Se modificó el método `StartClientLoop()` para que ahora se envíe una apuesta y luego termine, eliminando la lógica previa de timeouts(por el momento deja de ser un loop...).