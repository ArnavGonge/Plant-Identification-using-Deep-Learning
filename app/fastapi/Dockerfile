# Use an official Debian image
FROM python:3.10.12-slim

ENV PYTHONBUFFERED = 1

# Install system dependencies
RUN apt update && apt install -y gcc default-libmysqlclient-dev libxslt-dev pkg-config

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app/
COPY requirements.txt /app/

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app/
COPY . /app/

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
