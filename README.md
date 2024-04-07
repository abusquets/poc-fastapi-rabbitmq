# poc-fastapi-rabbitmq

The aim of this project is use a RabbitMQ consumer and Fastapi together to save infrastructure ressources.

I just found the amazing package https://faststream.airt.ai/, which does it all for you.

env for vscode
```
poetry env use 3.12
poetry install
```

Start service

```
docker-compose up
```


Publish a message

http://localhost:8080/hello
