import socket

# Função para enviar um comando ao servidor
def send_command(client_socket, command):
    client_socket.send(command.encode())

# Função para enviar um arquivo para o servidor
def send_file(client_socket, file_name):
    with open(file_name, 'rb') as file:
        data = file.read(1024)
        while data:
            client_socket.send(data)
            data = file.read(1024)

# Função principal
def main():
    # Configurações do servidor
    server_host = 'localhost'  # Endereço IP do servidor
    server_port = 9999  # Porta do servidor

    # Cria um socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Estabelece conexão com o servidor
    client_socket.connect((server_host, server_port))

    try:
        while True:
            # Recebe o comando do usuário
            command = input("Enter command (list, get <filename>, put <filename>, mkdir <dirname>, cd <dirname>, pwd, quit): ")
            send_command(client_socket, command)

            # Divide o comando em partes (comando e argumento)
            parts = command.split()
            action = parts[0].lower()

            if action == "list":
                # Recebe e imprime a lista de arquivos do servidor
                file_list = client_socket.recv(4096).decode()
                print("Files on server:")
                print(file_list)

            elif action == "get":
                # Recebe e salva o arquivo do servidor
                file_name = parts[1]
                with open(file_name, 'wb') as file:
                    data = client_socket.recv(1024)
                    while data:
                        file.write(data)
                        data = client_socket.recv(1024)
                print(f"File '{file_name}' downloaded successfully.")

            elif action == "put":
                # Envia um arquivo do cliente para o servidor
                file_name = parts[1]
                send_file(client_socket, file_name)
                print(f"File '{file_name}' uploaded successfully.")

            elif action == "mkdir":
                # Cria um diretório no servidor
                directory_name = parts[1]
                print(f"Creating directory '{directory_name}' on server...")
                f = client_socket.recv(1024).decode()
                print(f"{f}")

            elif action == "cd":
                # Altera o diretório atual do cliente no servidor
                directory_name = parts[1]
                print(f"Changing directory to '{directory_name}' on server...")
                f = client_socket.recv(1024)

            elif action == "pwd":
                # Exibe o diretório atual do servidor
                current_dir = client_socket.recv(1024).decode()
                print(f"Current directory on server: {current_dir}")

            elif action == "quit":
                # Encerra a conexão com o servidor e sai do loop
                break

    except KeyboardInterrupt:
        # Intercepta o sinal de interrupção (Ctrl+C) e encerra o cliente
        print("\n[*] Exiting...")
    finally:
        # Fecha o socket do cliente
        client_socket.close()

if __name__ == "__main__":
    main()
