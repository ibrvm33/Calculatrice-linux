import sys
import aioconsole
import asyncio
from pathlib import Path

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

async def as_input(reader, writer):
    while True:
        lines = []
        while True:
            user_input = await aioconsole.ainput()
            if not user_input:
                break
            lines.append(user_input)
        message = '\n'.join(lines)
        writer.write(message.encode())
        await writer.drain()

async def as_receive(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break
        message = data.decode()
        if "ID|" in message:
            with open('/tmp/idServ', 'w+') as f:
                f.write(message.split('|')[1])
        else:
            print(message)

async def main():
    reader, writer = await asyncio.open_connection(host="10.1.1.22", port=8888)
    try:
        pseudo = input("Enter your username: ")
        user_id = ''
        id_file = Path('/tmp/idServ')
        if id_file.exists():
            user_id = '|'
            with open('/tmp/idServ', 'r') as f:
                user_id += f.read()

        writer.write(f'Hello|{pseudo}{user_id}'.encode())
        await writer.drain()
        
        tasks = [as_input(reader, writer), as_receive(reader, writer)]
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print(BColors.FAIL + "Interruption de l'application" + BColors.ENDC)
        writer.write(b'&<END>')
        return
    finally:
        writer.close()
        await writer.wait_closed()
        print("Connexion fermée")

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)