# Delivery Service


## Package Registration Service
A FastAPI REST service that uses MySQL, Redis, Pydantic, SQLAlchemy, and async pytests, built as a Docker Compose microservice.

## Features
### Package Registration
Register new packages with their details: name, type, weight, value.

### View Registered Packages
- Retrieve a list of all package types and their id.
- Retrieve a list of all registered packages of a certain user.
- Retrieve a package's data by package id.

## Periodic Task
A scheduled task that updates the delivery costs for packages in the database by fetching the current USD to RUB exchange rate and recalculating costs. This task runs every 5 minutes.

## Getting Started
### Running the Service
Start Docker Compose.
Open a web browser and navigate to http://127.0.0.1:8000/documentation to access the Swagger documentation with protocol and RPC types.
### Running Tests
Open PyCharm.
Select the Docker Compose interpreter.
Run all tests in the tests folder.
Note: Make sure you have Docker Compose installed and configured on your system.
