# Use the official Python image with version 3.12 as the base image
FROM python:3.12-slim
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

USER root
RUN chmod 777 /app
RUN mkdir -p /.cache && chmod -R 777 /.cache
# Expose the port on which the Flask app will run
EXPOSE 5000

# Set the entrypoint command to run the Flask app
CMD ["python", "app.py"]