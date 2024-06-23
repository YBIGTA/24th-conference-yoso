#! /usr/bin/env bash

alembic upgrade head

fastapi run app/main.py --port 80
