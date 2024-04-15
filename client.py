import os
import socket


# Função para enviar um comando ao servidor
def send_command(client_socket, command):
    client_socket.send(command.encode())


# Função para enviar um arquivo para o servidor
def send_file(client_socket, file_name):
    try:
        # Envia o nome do arquivo para o servidor
        client_socket.send(file_name.encode())

        # Abre o arquivo para leitura em modo binário
        with open(file_name, 'rb') as file:
            # Lê os dados do arquivo e envia para o servidor
            data = file.read(1024)
            while data:
                client_socket.send(data)
                data = file.read(1024)

        client_socket.send('__EOF__'.encode())
        # retorno = client_socket.recv(1024)
        # print(retorno)

    except Exception as e:
        print(f"Error: {e}")

# Função que mostra na tela os comandos
def print_help():
    print("list --local             : List items on current folder locally\n"
          "list --remote            : List items on current folder on server\n"
          "get <filename>           : Download file locally from on server\n"
          "put <filename>           : Semd local file to on server\n"
          "mkdir <dirname> --local  : Create a folder locally\n"
          "mkdir <dirname> --remote : Create a folder on server\n"
          "cd <dirname> --local     : Navigate between folders, .. to get to parent folder locally\n"
          "cd <dirname> --remote    : Navigate between folders, .. to get to parent folder on server\n"
          "pwd --local              : Show current path locally\n"
          "pwd --remote             : Show current path on server\n"
          "--help                   : Show available commands\n"
          "quit                     : Leave client\n")


# Função principal
def main():
    # Configurações do servidor
    server_host = 'localhost'  # Endereço IP do servidor
    server_port = 9999  # Porta do servidor

    # Cria um socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Estabelece conexão com o servidor
    client_socket.connect((server_host, server_port))

    current_dir = os.getcwd()

    try:
        while True:
            # Recebe o comando do usuário
            command = input("Enter command: ")

            # Divide o comando em partes (comando e argumento)
            parts = command.split()
            if len(parts) == 1 and parts[0].lower() == '--help':
                print_help()
                continue

            action = parts[0].lower()

            if action == "list":
                if len(parts) < 2:
                    print("Command incomplete")
                    continue

                if parts[1] == "--local":
                    os.listdir()
                    files = os.listdir(current_dir)
                    file_list = "\n".join(files)
                    print(file_list)

                elif parts[1] == "--remote":
                    send_command(client_socket, command)

                    # Recebe e imprime a lista de arquivos do servidor
                    file_list = client_socket.recv(4096).decode()
                    print("Files on server:")
                    print(file_list)

                else:
                    print("Command invalid")

            elif action == "get":
                send_command(client_socket, command)

                # Recebe e salva o arquivo do servidor
                file_name = parts[1]
                with open(file_name, 'wb') as file:
                    data = client_socket.recv(1024)
                    while data:
                        if data.endswith(b'__EOF__'):
                            file.write(data[7:])
                            break
                        file.write(data)
                        data = client_socket.recv(1024)
                print(f"File '{file_name}' downloaded successfully.")

            elif action == "put":
                send_command(client_socket, command)

                # Envia um arquivo do cliente para o servidor
                file_name = parts[1]

                client_socket.send(file_name.encode())

                # Abre o arquivo para leitura em modo binário
                with open(file_name, 'rb') as file:
                    # Lê os dados do arquivo e envia para o servidor
                    data = file.read(1024)
                    client_socket.send(data)

                # Adiciona fim do arquivo a mensagem
                client_socket.send('__EOF__'.encode())

                # send_file(client_socket, file_name)
                print(f"File '{file_name}' uploaded successfully.")

            elif action == "mkdir":
                if len(parts) < 3:
                    print("Command incomplete")
                    continue

                directory_name = parts[1]
                subaction = parts[2]

                if subaction == "--local":
                    os.makedirs(directory_name, exist_ok=True)
                    if os.path.isdir(directory_name):
                        print(f"Directory '{directory_name}' created.")
                    else:
                        print(f"Directory '{directory_name}' not created.")

                elif subaction == "--remote":
                    send_command(client_socket, command)

                    # Cria um diretório no servidor
                    print(f"Creating directory '{directory_name}' on server...")
                    f = client_socket.recv(1024).decode()
                    print(f"{f}")

                else:
                    print("subação inválida")

            elif action == "cd":
                if len(parts) < 3:
                    print("Command incomplete")
                    continue

                directory_name = parts[1]
                option = parts[2]

                if option == "--local":

                    if directory_name == "..":
                        current_dir = os.path.dirname(current_dir)
                        client_socket.send(current_dir.encode())
                    else:
                        new_dir = os.path.join(current_dir, directory_name)

                        if os.path.isdir(new_dir):
                            current_dir = new_dir
                            client_socket.send(current_dir.encode())
                        else:
                            print("Directory not found")

                elif option == "--remote":
                    # Altera o diretório atual do cliente no servidor
                    send_command(client_socket, command)
                    print(f"Changing directory to '{directory_name}' on server...")
                    f = client_socket.recv(1024)

                else:
                    print("Command invalid")

            elif action == "pwd":
                if len(parts) < 2:
                    print("Command incomplete")
                    continue

                option = parts[1]

                if option == "--local":
                    print(f"Current directory locally: {current_dir}")

                elif option == "--remote":
                    send_command(client_socket, command)

                    # Exibe o diretório atual do servidor
                    current_dir_server = client_socket.recv(1024).decode()
                    print(f"Current directory on server: {current_dir_server}")

                else:
                    print("Command invalid")

            elif action == "quit":
                # Encerra a conexão com o servidor e sai do loop
                break

            else:
                print("Command invalid")

    except KeyboardInterrupt:
        # Intercepta o sinal de interrupção (Ctrl+C) e encerra o cliente
        print("\n[*] Exiting...")
    finally:
        # Fecha o socket do cliente
        client_socket.close()


if __name__ == "__main__":
    main()
