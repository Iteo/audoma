FROM python:3.9-bullseye

RUN mkdir audoma
WORKDIR /audoma
COPY ./requirements.txt /audoma/requirements.txt
COPY ./requirements_dev.txt /audoma/requirements_dev.txt


RUN apt-get update && \
      apt-get -y install sudo
RUN sudo apt-get install -y python3-dev libpq-dev
RUN pip install --upgrade pip
RUN pip install -r /audoma/requirements_dev.txt

RUN git clone https://github.com/pyenv/pyenv /root/.pyenv
RUN /root/.pyenv/bin/pyenv install 3.7.13  && /root/.pyenv/bin/pyenv install 3.8.12 && /root/.pyenv/bin/pyenv install 3.9.7
RUN /root/.pyenv/bin/pyenv local 3.7.13 3.8.12 3.9.7

ADD ./ /audoma
RUN pip install .
