# DDD Architecture Practice Project

This project implements Domain-Driven Design (DDD) patterns (like the Repository Pattern, Service Layer, and Unit of Work) to create a robust, decoupled architecture in Python.

## Setting up for Local Development

The project is structured into three tiers of testing. Because our E2E tests and some Integration tests run against a real database to ensure high fidelity, you need to spin up the required local infrastructure before testing.

### 1. Boot up Local Infrastructure

We use `docker-compose` to run the database and API locally, completely detached from Kubernetes. Start the environment by running:

```bash
docker compose up -d --build
```
This spins up:
- A PostgreSQL 9.6 container on port `5432`
- The Flask API container on port `5005`

### 2. Run the Test Suite

With the environment running, you can now run the complete test suite. The Pytest fixtures will automatically connect to your local Docker containers for the E2E tests:

```bash
pytest
```
*Note: If you run `pytest` without starting Docker Compose first, the E2E tests will automatically fail gracefully after timing out while trying to reach the database/API.*

### 3. Tearing Down

When you are done developing, you can tear down the local environment:

```bash
docker compose down
```

## Further Reading

- [The Testing Pyramid & Repository Pattern](./testing_pyramid.md) - Explains why we structure our tests this way.
- [E2E Testing Architecture](./e2e_testing_walkthrough.md) - A deep dive into how the Pytest fixtures orchestrate the test data and connect to the Docker containers.
