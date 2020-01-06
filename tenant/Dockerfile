FROM tiangolo/uvicorn-gunicorn-starlette:python3.7-alpine3.8

COPY ./requirements.txt requirements.txt

RUN pip install -U -r requirements.txt

COPY ./app /app
