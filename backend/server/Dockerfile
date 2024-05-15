FROM python:3.12

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./server /app/server

CMD ["fastapi", "run", "server/main.py", "--port", "80"]
