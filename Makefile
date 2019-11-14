include .env

default: build

build:
	@docker build --rm --build-arg PYTHON_VER=${PYTHON_VER} \
			--rm --build-arg LIBCITISIM_VER=${LIBCITISIM_VER} \
			-t citisim-kafka-adapter:${DOCKER_IMAGE_TAG} .

compose:
	@docker-compose build && docker-compose up
