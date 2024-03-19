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
