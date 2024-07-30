FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
WORKDIR /code/src