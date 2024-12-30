FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /worker

# Copy the main app folder into the container
COPY ./app ./app

# Copy the main requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the worker script can find the app modules
ENV PYTHONPATH="${PYTHONPATH}:/worker/app"

# Set the default command to run the worker process
CMD ["python", "app/worker/worker.py"]
