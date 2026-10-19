import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()['count'] == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Buy milk", False))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Finish FlyRank assignment", False))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Read a book", True))
    conn.commit()
    cursor.close()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Containerized Task API", lifespan=lifespan)

class Task(BaseModel):
    title: str
    done: bool = False

class TaskResponse(Task):
    id: int

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "4.0", "endpoints": ["/tasks"]}

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *", 
        (task.title, task.done)
    )
    new_task = cursor.fetchone()
    conn.commit()
    conn.close()
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *", 
        (task.title, task.done, task_id)
    )
    updated_task = cursor.fetchone()
    conn.commit()
    conn.close()
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
    deleted = cursor.fetchone()
    conn.commit()
    conn.close()
    if deleted is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return
