# Use an official Python runtime as a parent image
#FROM python:3.12-slim
FROM tiangolo/uvicorn-gunicorn-fastapi

RUN apt update && apt install -y git build-essential
# Set the working directory in the container
RUN pip install redis git+https://github.com/long2ice/asyncmy.git@v0.2.9 fastapi-utils[all]

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r ./requirements.txt
# Set environment variables, if needed (e.g., PYTHONPATH)
ENV PYTHONPATH=/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Command to start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]