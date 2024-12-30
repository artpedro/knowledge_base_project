# Use Python as base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /scraper

# Copy requirements and install dependencies
COPY requirements-scrapy.txt .
RUN pip install --no-cache-dir -r requirements-scrapy.txt

# Copy Scrapy project files
COPY . .

# Set default command to run Scrapy spiders
CMD ["scrapy", "crawl", "kdnuggets"]