from psgdb import Base
from sqlalchemy import Column, String, ForeignKey, Integer


# Define the Employee model
class Employee(Base):
    __tablename__ = "employees"

    email = Column(String, primary_key=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    manager = Column(String, ForeignKey("employees.email"), default=None)
    role = Column(String)


# Define the Tasks
class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="open")
    reporter = Column(String, ForeignKey("employees.email"))
    assignee = Column(String, ForeignKey("employees.email"))
    priority = Column(Integer)
