-- DELETE TABLE employees if it already exists
DROP TABLE IF EXISTS employees;

-- CREATE TABLE employees
CREATE TABLE employees (
    email VARCHAR(100) PRIMARY KEY,
    password VARCHAR(200) NOT NULL,
    first_name VARCHAR(30) DEFAULT NULL,
    last_name VARCHAR(30) DEFAULT NULL,
    manager VARCHAR(100) DEFAULT NULL,
    role VARCHAR(20),
    FOREIGN KEY (manager) REFERENCES employees(email)
);

-- DELETE TABLE tasks if it already exists
DROP TABLE IF EXISTS tasks;

-- CREATE TABLE tasks
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(200) DEFAULT NULL,
    status VARCHAR(20),
    reporter VARCHAR(100) NOT NULL,
    assignee VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY (reporter) REFERENCES employees(email),
    FOREIGN KEY (assignee) REFERENCES employees(email),
    priority Integer
);

-- ADD ADMIN USER
INSERT INTO employees VALUES ('admin@domain.com', 'password', 'admin', 'admin', Null, 'admin');
