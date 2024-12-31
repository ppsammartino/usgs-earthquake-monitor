# USGS Earthquake Monitor

This project provides a full-stack application to search for and display the nearest earthquakes above a certain magnitude from the USGS dataset for specified cities and date ranges.

## Overview

- **Backend (API)**: Django + Django REST Framework, PostgreSQL database, Redis caching.
- **Frontend**: React application that consumes the API.
- **Documentation**: Swagger UI for API endpoints.

## Features

- Create and store city data (name and coordinates).
- Query USGS Earthquake API for earthquakes in a given date range (above magnitude 5.0 by default).
- Determine the closest earthquake to a specified city.
- Cache results to improve performance and reduce repeated external API calls.
- View API documentation via Swagger UI.

## Prerequisites

- Docker and docker-compose installed on your machine.

## Setup and Run

1. **Set environment variables**: Edit .env file to set SECRET_KEY, DB_USER, DB_PASSWORD, etc.
The defaults work for local development.

2. **Build and start the services**:

    ```bash
    make build
    make up
    ```
    This starts:
    
    The Django API at http://localhost:8000

    The React frontend at http://localhost:3000

    PostgreSQL and Redis run as background services.

3. **Run database migrations and create a superuser:**

   On a new terminal, run
    ```bash
    make migrate
    make createsuperuser
    ```


## API Endpoints:

All available API endpoints are listed in the **Swagger UI**: http://localhost:8000/swagger/

The Swagger UI provides a web interface to explore and test all API endpoints.

### Interacting with the API:
Below are a few examples of API requests

#### Create a City:

```bash
curl -X POST http://localhost:8000/api/cities/ \
-H "Content-Type: application/json" \
-d '{"name":"Los Angeles","latitude":34.0522,"longitude":-118.2437}'
```
#### Search for Earthquakes:

```bash
curl "http://localhost:8000/api/earthquakes/?city_id=1&start=2021-06-01&end=2021-07-05"
```

## Using the Makefile
* **make build**: Build all services
* **make up**: Start all containers (api, frontend, db, redis)
* **make makemigrations**: Create Django migrations for model changes
* **make migrate**: Apply Django migrations
* **make createsuperuser**: Create a Django superuser
* **make down**: Stop containers
* **make logs**: Tail logs of all services
* **make test**: Runs all the API tests
* **make lint-py**: Runs black/flake8 linting for API
* **make lint-fe**: Runs eslint for the frontend
* **make lint**: Runs lint-py and lint-fe
* **make fix-formatting**: Runs a fix formatting script for API

## Notes
For a production setup, consider:
* Setting DEBUG=0 in .env.
* Using a secure, non-committed SECRET_KEY.
* Externalizing and securing database credentials.