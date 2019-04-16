FROM python:3
# Install libraries
RUN apt-get update -y && apt-get dist-upgrade -y
RUN apt-get install -y mysql-server default-libmysqlclient-dev
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt
