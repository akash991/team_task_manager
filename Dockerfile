FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY app/ .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE the port the app runs on
EXPOSE 8000

# Command to run the application
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload" ]
