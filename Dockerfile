# Declaration of PYTHON_VER
ARG PYTHON_VER

# When install zeroc-ice dependency we need to build it
FROM python:${PYTHON_VER} AS IceBuilder
RUN pip install zeroc-ice

# Re-declaration of PYTHON_VER (https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact)
ARG PYTHON_VER

# Create citisim kafka connector
FROM python:${PYTHON_VER}-slim
WORKDIR /opt/citisim

# Re-declaration of PYTHON_VER
ARG PYTHON_VER
# Declaration of LIBCITISIM_VER
ARG LIBCITISIM_VER

# Copy Zeroc-Ice libraries to new image
COPY --from=IceBuilder /usr/local/lib/python${PYTHON_VER}/site-packages /usr/local/lib/python${PYTHON_VER}
# Copy libcitisim project
COPY libcitisim-${LIBCITISIM_VER}.tar.gz ./
# Copy requirements
COPY requirements.txt ./

# Extract slices, install dependencies
RUN tar --wildcards --strip-components=1 -xvf libcitisim-${LIBCITISIM_VER}.tar.gz --directory /usr/share libcitisim-*/slice \
    && pip install -r requirements.txt \
    && rm -rf libcitisim-${LIBCITISIM_VER}.tar.gz requirements.txt

COPY kafka-mirror ./
COPY start.sh ./

ENV KAFKA_BROKER=localhost:9092

CMD /opt/citisim/start.sh 
