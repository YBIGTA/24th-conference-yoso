FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

COPY ./alembic.ini /code/alembic.ini

COPY ./entrypoint.sh /code/entrypoint.sh

RUN chmod +x /code/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
