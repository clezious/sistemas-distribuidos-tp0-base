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