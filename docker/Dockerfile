FROM python:3.9-buster

RUN mkdir audoma
WORKDIR /audoma
COPY ./requirements/base.txt /audoma/requirements/base.txt
COPY ./requirements/dev.txt /audoma/requirements/dev.txt
RUN pip install --upgrade pip
RUN pip install -r /audoma/requirements/dev.txt

RUN git clone https://github.com/pyenv/pyenv /root/.pyenv
RUN /root/.pyenv/bin/pyenv install 3.7.13  && /root/.pyenv/bin/pyenv install 3.8.12 && /root/.pyenv/bin/pyenv install 3.9.7
RUN /root/.pyenv/bin/pyenv local 3.7.13 3.8.12 3.9.7

ADD ./ /audoma
