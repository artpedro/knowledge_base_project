# Use Python as base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /scraper

# Copy requirements and install dependencies
COPY requirements-scrapy.txt .
RUN pip install --no-cache-dir -r requirements-scrapy.txt

# Copy all Scrapy project files
COPY . .

# Set the environment variables for Redis connection
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Default command to run the Redis listener

CMD ["python", "listener.py"]