# Containerized CRUD API (FlyRank BE-04)

This is the Stage 2 CRUD API, now fully containerized. The in-memory/SQLite repository has been swapped for a PostgreSQL database running in a Docker container. 

**Crucially, the API service layer and routing logic remained exactly the same.** The client cannot tell the underlying storage layer has changed.

## Setup & Run Instructions
1. Ensure Docker Desktop is installed and running.
2. Clone this repository.
3. Run the following command in the terminal at the root of the project:
   `docker compose up --build`
4. The API will be available at `http://localhost:8000/docs`.

## Proof of Persistence
Data persistence is achieved via a Docker volume (`pgdata`). To verify:
1. Open Swagger UI (`http://localhost:8000/docs`) and POST a new task.
2. Stop the containers by pressing `Ctrl+C` in the terminal, or running `docker compose down`.
3. Restart the containers with `docker compose up`.
4. Run a GET request to `/tasks`. The task you created before the restart will still be there.
