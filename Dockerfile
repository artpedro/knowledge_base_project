# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-flask.txt .
RUN pip install --no-cache-dir -r requirements-flask.txt

# Copy application code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Define the entrypoint
CMD ["python", "run.py"]
