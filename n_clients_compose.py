import sys

SERVER_SERVICE = """
    server:
        container_name: server
        image: server:latest
        entrypoint: python3 /main.py
        environment:
            - PYTHONUNBUFFERED=1
            - LOGGING_LEVEL=DEBUG
        networks:
            - testing_net
"""

TESTING_NET = """
    testing_net:
        ipam:
            driver: default
            config:
            - subnet: 172.25.125.0/24
"""


def generate_compose(num_clients, filename):
    clients = get_client_services(num_clients)
    content = f"""
version: '3.9'
name: tp0
services:
    {SERVER_SERVICE}
    {clients}
networks:
    {TESTING_NET}
    """
    with open(filename, 'w') as f:
        f.write(content)


def get_client_services(num_clients):
    clients = ''
    for i in range(1, num_clients + 1):
        clients += f"""
    client{i}:
        container_name: client{i}
        image: client:latest
        entrypoint: /client
        environment:
            - CLI_ID={i}
            - CLI_LOG_LEVEL=DEBUG
        networks:
            - testing_net
        depends_on:
            - server
"""
    return clients


def main():
    num_clients = int(sys.argv[1])
    if len(sys.argv) != 2:
        print('Usage: python n_clients_compose.py <n>')
        return
    if num_clients < 1:
        print('n must be >= 1')
        return
    filename = 'docker-compose-dev.yaml'
    generate_compose(num_clients, filename)


if __name__ == '__main__':
    main()
