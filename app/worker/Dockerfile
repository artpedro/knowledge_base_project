# Use Python as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /worker

# Copy only the requirements file
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app ./app

# Set the environment variable for Python path
ENV PYTHONPATH="/worker"

# Default command to run the worker
CMD ["python","app/worker/worker.py"]