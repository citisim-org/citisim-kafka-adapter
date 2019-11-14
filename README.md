# Citisim Kafka Adapter

This repo contains files to generate an image to forward events from citisim to Kafka.

## Requirements

Before to build the docker image we need download latest version for [libcitisim](https://bitbucket.org/arco_group/libcitisim/src/master/).

## Build

To build this project you only need to run the next command:

```
make
```

This command will create a new docker image named `citisim-kafka-adapter:<DOCKER_IMAGE_TAG>`. Next, you can see the default values defined in `.env` file used to create the docker image.

|Variable   |Default Value   |Description   |
|:-:|:-:|---|
|PYTHON_VER   |3.6   |Python docker image base  |
|LIBCITISIM_VER   |latest   |Downloaded libcititism library version from its Bitbucket repo   |
|DOCKER_IMAGE_TAG   |latest   |Docker image tag   |

## Run

You must run the next command to use minimal `kafka-mirror` configuration

```
docker run --name citisim2kafka -e KAFKA_BROKER="10.0.150.70:9092" citisim-kafka-adapter:latest
```

or use the docker compose file:

```
docker-compose up -d
```

Next, you can see the default configuration in `.env` file:

|Variable   |Default Value   |Description   |
|:-:|:-:|---|
|KAFKA_BROKER   |127.0.0.1:9092   |Kafka broker server  |
|TOPIC  |none  |libcitisim topic subcriptions and kafka topic publish  |

