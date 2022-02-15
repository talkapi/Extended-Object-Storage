# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
EXPOSE 8090
WORKDIR /src/

COPY requirements.txt requirements.txt
COPY swagger.yaml swagger.yaml
RUN pip3 install -r requirements.txt

# Copy the content of our server to the container
COPY . .

CMD [ "python3", "main.py"]