import asyncio
import random
from os import environ
from pprint import pprint
from pathlib import Path

CLIENTS = {}
port = int(environ.get("CHAT_PORT", 8888))

def generate_id(length):
    id_str = ''
    while length > 8:
        comp = 9 if length > 9 else length
        id_str += str(hex(random.randrange(1, 10**comp)))[2:]
        length -= 9
    return id_str

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def handle_client_msg(reader, writer):
    pseudo, client_id = '', ''
    addr = writer.get_extra_info('peername')

    while True:
        data = await reader.read(1024)
        if not data:
            break

        message = data.decode()
        new_user = False

        if message.startswith('Hello|'):
            parts = message.split('|')
            if len(parts) == 2:
                print('New user received')
                pseudo = parts[1]
                client_id = generate_id(100)
                writer.write(f"ID|{client_id}".encode())
                new_user = True
            elif len(parts) > 2:
                print('Existing user reconnecting')
                pseudo = parts[1]
                client_id = parts[2]
                new_user = True
        elif message == '&<END>':
            print('Client leaving')
            if client_id in CLIENTS:
                for ids in CLIENTS:
                    CLIENTS[ids]['w'].write(f"{BColors.OKBLUE}{CLIENTS[client_id]['pseudo']} {BColors.WARNING} left the Chatroom {BColors.ENDC}".encode())
                    await CLIENTS[ids]['w'].drain()
                CLIENTS.pop(client_id, None)
            break

        CLIENTS[client_id] = {'w': writer, 'r': reader, 'LastAdress': addr, 'pseudo': pseudo}
        
        for ids in CLIENTS:
            if new_user:
                CLIENTS[ids]['w'].write(f"{BColors.OKBLUE}{pseudo} {BColors.HEADER} has joined{BColors.ENDC}".encode())
            elif ids != client_id:
                print(f"{pseudo} sending to {CLIENTS[ids]['pseudo']}")
                mess_list = message.split("\n")
                prefix = f"{BColors.OKBLUE}{pseudo} {BColors.HEADER}:> "
                CLIENTS[ids]['w'].write(f"{prefix}{mess_list[0]}{BColors.ENDC}".encode())
                for line in mess_list[1:]:
                    CLIENTS[ids]['w'].write(f"\n{' ' * len(prefix)}{BColors.HEADER}{line}{BColors.ENDC}".encode())
                CLIENTS[ids]['w'].write(b"\n")
                await CLIENTS[ids]['w'].drain()
            else:
                print("Message not sent to self")

async def main():
    server = await asyncio.start_server(handle_client_msg, '127.0.0.1', port)
    print(f'Serving on {', '.join(str(sock.getsockname()) for sock in server.sockets)}')
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())