FROM python:3.9-buster

RUN mkdir audoma
WORKDIR /audoma
COPY ./requirements.txt /audoma/requirements.txt
COPY ./requirements_dev.txt /audoma/requirements_dev.txt
RUN pip install --upgrade pip
RUN pip install -r /audoma/requirements_dev.txt

RUN git clone https://github.com/pyenv/pyenv /root/.pyenv
RUN /root/.pyenv/bin/pyenv install 3.7.13  && /root/.pyenv/bin/pyenv install 3.8.12 && /root/.pyenv/bin/pyenv install 3.9.7
RUN /root/.pyenv/bin/pyenv local 3.7.13 3.8.12 3.9.7

ADD ./ /audoma
RUN pip install .
