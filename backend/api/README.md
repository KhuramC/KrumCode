# API

This directory holds server and API for querying the RAG model.

## Structure

- [main.py](./main.py): the middleware for what can connect to the server.
- [rest.py](./rest.py): the REST API endpoints.
- [run.py](./run.py): running the server.

## Important Commands

Within the backend directory, assuming everything is up to date, one can run
`poetry run server` to start the FastAPI server. FastAPI has an easy way to test the server by going to `docs` like this: [http://host:port_number/docs](http://localhost:8000/docs) once it is running.
