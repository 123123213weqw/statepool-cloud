FROM nvidia/cuda:12.4.1-base-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN rm -f /etc/apt/sources.list.d/cuda*.list && \
    sed -i -e 's#http://archive.ubuntu.com/ubuntu#https://mirrors.cloud.tencent.com/ubuntu#g' \
           -e 's#http://security.ubuntu.com/ubuntu#https://mirrors.cloud.tencent.com/ubuntu#g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-dev build-essential ca-certificates curl libnuma1 libgomp1 && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3.10 /usr/local/bin/python && \
    ln -sf /usr/bin/gcc /usr/local/bin/cc
ENTRYPOINT ["/usr/bin/python3.10"]
