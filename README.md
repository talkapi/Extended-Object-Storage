# Introduction
Please install all packages in requirements.txt file.

## Run in Docker
```sh
docker build -t imagename .
docker run --env-file=.env -it --rm -p 8094:8094 --name continerName imagename
```
