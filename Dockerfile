FROM python
COPY server.py ./
ENV CHAT_PORT=8888
ENV MAX_USERS=10
ENTRYPOINT ["python","server.py"]