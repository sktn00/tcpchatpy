import socket    # Look into it
import threading # Look into it

host = '127.0.0.1' # localhost
port = 22222

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Use an IPv4 internet (INET) socket + TCP (SOCK_STREAM)
server.bind((host, port)) # Bind the sockets to the selected host + port
server.listen() # Server function

clients = []
nicknames = []

def broadcast(message):
    # Sends a message to all the clients connected
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            # We receive messages from the client, whatever we receive we broadcast
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused.'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned.')
                else:
                    client.send('Command was refused.'.encode('ascii'))
            else:
                broadcast(message)
        except:  # noqa: E722
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} has left the chat.'.encode('ascii'))
                nickname.remove(nickname)
                break

def receive():
    while True:
        client, address = server.accept()   # Accept clients all the time
        print(f'Connected with {str(address)}') # When a client connects we print this so the server admin knows.

        client.send('NICK'.encode('ascii')) # Request the client for his nick

        nickname = client.recv(1024).decode('ascii') # Receive his nick

        with open('bans.txt', 'r') as f:
                  bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'admin123':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname) # Append this nickname to our list
        clients.append(client)  # Append this client to our list

        print(f'Nickname of the client is {nickname}') # Print for the server admin
        broadcast(f'{nickname} joined the chat.'.encode('ascii')) # Broadcast to all the clients connected to the server that this client with this nickname joined the chat
        client.send('Connected to the server!'.encode('ascii')) # Send a message to the particular client that the connection was successful

        thread = threading.Thread(target=handle, args=(client,)) # Start a thread handling the connection to this particular client
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin.'.encode('ascii'))

print('Server is ready...')
receive()