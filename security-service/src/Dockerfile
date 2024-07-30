FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /wss
WORKDIR /wss
COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
WORKDIR /wss/src