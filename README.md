# Overview

![2140_bot](./resources/cover.png)

Get the meetups information in a interactive way in the [telegram group](https://t.me/+OIK8Yq6ZhbE3NzQ0)

## Spin up the project

__Requirements__: Docker installed

```bash
# Build the container
docker compose build
# Two-in-one: Build and start the container. The brackets block is optional
docker compose up [--build]
```

## Dockerfile (TODO)

We cannot spin up the container just using the `Dockerfile`. Future implementation will work just with that file. From now, we use `docker-compose.yml`

```bash
# NOT working...
docker build -t 2140-bot .
docker run --rm  -v ./bot:/usr/local/ --name bot_container 2140-bot
```