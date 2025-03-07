# Calculatrice-linux

**Build**

    docker build -t chat .

**up**

    docker compose up 

**modif port d'ecoute**

    docker run -e CHAT_PORT=6767 -d chat