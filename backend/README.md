# YOSO Backend

Backend application for [**You Only Search Once**](https://github.com/paper-writing-assistance/you-only-search-once) built with FastAPI, featuring several databases and managed cloud services including Pinecone, MongoDB Atlas, PostgreSQL, and Neo4j. Alembic is also used for database migrations and Docker Compose for container orchestration.

## Introduction
The main functionalities of the application are:
- Handle user queries based on similarity search using Pinecone and retrieve related data from MongoDB and Neo4j
- Store paper metadata

## Features
- ⚡️ **FastAPI**: Python backend.
- 🌲 **Pinecone**: Vector store for handling similarity search.
- 🍃 **MongoDB Atlas**: Document database for storing paper data.
- 🌐 **Neo4j**: Graph database for managing relationships among papers.
- 💾 **PostgreSQL**: Relational database for handling user information, authentication, etc.
- ⚗️ **Alembic**: Database migration tool for use with SQLAlchemy/SQLModel.
- 🐳 **Docker Compose**: For defining and running multi-container application.


## Prerequisites
- Docker: `26.1.4+`
- Python: `3.12.3+`

## Getting Started
1. Clone the repository
```bash
git clone https://github.com/paper-writing-assistance/backend
cd backend
```

2. Set up environment variables

Create a `.env` file in the root directory and add the required environment variables listed in `.env.example`:
```bash
PROJECT_NAME="You Only Search Once"

# FastAPI
BACKEND_CORS_ORIGINS=
SECRET_KEY=

# PostgreSQL
PGDATA=
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_DB=
...
```

3. Build and run the Docker containers
```bash
docker-compose up --build
```
This command will build and start the containers for FastAPI, PostgreSQL, and Neo4j. Once the Docker containers are up and running, you can access the application's API documentations at http://localhost/docs.

## Database Migrations

To create a new migration, run:
```bash
alembic revision --autogenerate -m "your migration message"
```

## Project Structure
```
├── app
│   ├── api
│   │   ├── routes
│   │   │   └── paper.py
│   │   ├── deps.py
│   │   └── main.py
│   ├── core
│   │   ├── config.py
│   │   ├── db.py
│   │   └── security.py
│   ├── migrations
│   │   ├── versions
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── crud.py
│   ├── main.py
│   ├── models.py
│   └── utils.py
├── .env
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── README.md
└── requirements.txt
```