from fastapi import FastAPI
from routers import admin, tasks, auth

app = FastAPI()

app.include_router(admin.router)
app.include_router(tasks.router)
app.include_router(auth.router)
