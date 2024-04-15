import socket
import threading
import os


# Função para lidar com cada cliente
def handle_client(client_socket, current_dir):
    try:
        while True:
            # Recebe o comando do cliente
            command = client_socket.recv(1024).decode()
            if not command:
                break

            # Divide o comando em partes (comando e argumento)
            parts = command.split()
            action = parts[0].lower()

            if action == "list":
                # Lista os arquivos no diretório atual do servidor
                files = os.listdir(current_dir)
                file_list = "\n".join(files)
                client_socket.send(file_list.encode())

            elif action == "get":
                # Verifica se o arquivo solicitado existe e envia seu conteúdo para o cliente
                file_name = parts[1]
                file_path = os.path.join(current_dir, file_name)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        data = file.read(1024)
                        while data:
                            client_socket.send(data)
                            data = file.read(1024)

                    client_socket.send("__EOF__".encode())
                else:
                    client_socket.send(b'File not found')



            elif action == "put":

                # Recebe o arquivo enviado pelo cliente e salva no servidor

                file_name = client_socket.recv(1024).decode()

                file_path = os.path.join(current_dir, file_name)

                with open(file_path, 'wb') as file:
                    while True:
                        data = client_socket.recv(1024)
                        print(data)
                        if data == b'':  # Verifica se a conexão foi fechada
                            break
                        if data.startswith(b'__EOF__'):  # Verifica se é o final do arquivo
                            file.write(data[7:])
                            break
                        file.write(data)

                # Envia a confirmação de que o arquivo foi recebido com sucesso

                #client_socket.send(f"File '{file_name}' uploaded successfully.".encode())

            elif action == "mkdir":
                # Cria um diretório no servidor
                directory_name = parts[1]
                directory_path = os.path.join(current_dir, directory_name)
                os.makedirs(directory_path, exist_ok=True)
                if os.path.isdir(directory_path):
                    client_socket.send(f"Directory '{directory_name}' created.".encode())
                else:
                    client_socket.send(f"Directory '{directory_name}' not created.".encode())

            elif action == "cd":
                # Altera o diretório atual do servidor
                directory_name = parts[1]

                if directory_name == "..":
                    current_dir = os.path.dirname(current_dir)
                    client_socket.send(current_dir.encode())
                else:
                    new_dir = os.path.join(current_dir, directory_name)

                    if os.path.isdir(new_dir):
                        current_dir = new_dir
                        client_socket.send(current_dir.encode())

                    else:
                        client_socket.send(b'Directory not found')

            elif action == "pwd":
                # Envia o diretório atual do servidor para o cliente
                client_socket.send(current_dir.encode())

            elif action == "quit":
                # Encerra a conexão com o cliente
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Fecha o socket do cliente
        client_socket.close()


# Função principal
def main():
    # Configurações do servidor
    server_host = '0.0.0.0'  # Escuta em todas as interfaces disponíveis
    server_port = 9999

    if not os.path.isdir("arquivos"):
        os.makedirs("arquivos", exist_ok=True)

    # Cria um socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Associa o socket com o endereço e porta do servidor
    server_socket.bind((server_host, server_port))
    # Coloca o socket em modo de escuta, permitindo conexões de até 5 clientes pendentes
    server_socket.listen(5)
    print(f"[*] Listening on {server_host}:{server_port}")

    try:
        # Define o diretório atual do servidor como o diretório raiz inicialmente
        current_dir = os.path.join(os.getcwd(), 'arquivos')

        # Loop principal para aceitar conexões de clientes
        while True:
            # Aceita a conexão do cliente
            client_socket, addr = server_socket.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

            #handle_client(client_socket, current_dir)
            # Cria uma nova thread para lidar com o cliente
            client_handler = threading.Thread(target=handle_client, args=(client_socket, current_dir))
            client_handler.start()
    except KeyboardInterrupt:
        # Intercepta o sinal de interrupção (Ctrl+C) e encerra o servidor
        print("\n[*] Exiting...")
        server_socket.close()


if __name__ == "__main__":
    main()
