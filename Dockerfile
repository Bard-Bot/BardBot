FROM ubuntu:18.04

ENV PYTHON_VERSION 3.8.3
ENV HOME /root
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_ROOT $HOME/local/python-$PYTHON_VERSION
ENV PATH $PYTHON_ROOT/bin:$PATH
ENV PYENV_ROOT $HOME/.pyenv
RUN apt-get update && apt-get upgrade -y \
 && apt-get install -y \
    git \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
 && git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT \
 && $PYENV_ROOT/plugins/python-build/install.sh \
 && /usr/local/bin/python-build -v $PYTHON_VERSION $PYTHON_ROOT \
 && rm -rf $PYENV_ROOT

RUN apt-get install -y opus-tools

WORKDIR /bot

ADD . /bot

RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install -U git+https://github.com/sizumita/discord.py.git

CMD ["python", "bard.py"]
