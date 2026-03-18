# ![RealWorld Example App](etc/images/logo.png)

> ### FastAPI codebase containing real world examples (CRUD, auth, advanced patterns, monitoring, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.build/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged fullstack application built with **FastAPI/SQLAlqhemy/OpenTelemetry** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **FastAPI** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.

## How it works

The application follows a layered architecture built with **FastAPI**, **SQLAlchemy** and **OpenTelemetry**:

- **API layer** (`conduit/api/routes/`) — FastAPI routers handling HTTP requests for users, articles, and profiles.
- **CRUD layer** (`conduit/crud/`) — Database operations.
- **Models layer** (`conduit/models.py`) — Models defining the database schema.
- **Schemas layer** (`conduit/schemas/`) — Pydantic models for request/response validation.
- **Core layer** (`conduit/core/`) — Configuration, database engine, and security utilities.

## Getting started

### Prerequisites

- [Python](https://www.python.org/) 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for running infrastructure services

### Environment Variables

Copy the example environment file and adjust values as needed:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `ALLOWED_CORS_ORIGINS` | List of allowed CORS origins | `["http://localhost:3000"]` |
| `DATABASE_URI` | PostgreSQL connection string | `postgresql://root:root@localhost:5432/test` |
| `SECRET_KEY` | Secret key for JWT token signing | — |
| `OTLP_GRPC_ENDPOINT` | OpenTelemetry Collector gRPC endpoint | `http://localhost:4317` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes | `120` |

### Running Locally (without Docker)

1. Install dependencies using [Poetry]:

```bash
poetry install
```

2. Activate the virtual environment:

```bash
poetry shell
```

3. Start the infrastructure services (PostgreSQL, OpenTelemetry Collector, etc.):

```bash
docker compose up -d postgres otel-collector pgadmin jaeger prometheus grafana opensearch
```

4. Make sure your `.env` file points to the local services (see `.env.example`).

5. Start the application using [Uvicorn]:

```bash
uvicorn conduit.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API docs are served at `http://localhost:8000/docs`.

### Running with Docker Compose

The easiest way to run the entire stack (application + infrastructure) is using Docker Compose:

1. Build and start all services:

```bash
docker compose up -d --build
```

This will start the following services:

| Service | URL | Description |
|---|---|---|
| **conduit-backend** | http://localhost:8000 | FastAPI application |
| **postgres** | localhost:5432 | PostgreSQL database |
| **pgadmin** | http://localhost:5050 | Database administration UI |
| **jaeger** | http://localhost:16686 | Distributed tracing UI |
| **otel-collector** | localhost:4317 (gRPC) / localhost:4318 (HTTP) | OpenTelemetry Collector |
| **prometheus** | http://localhost:9090 | Metrics storage and querying |
| **grafana** | http://localhost:3000 | Monitoring dashboards |
| **opensearch** | http://localhost:9200 | Log storage and search |

2. To stop all services:

```bash
docker compose down
```

3. To view logs for a specific service:

```bash
docker compose logs -f conduit-backend
```

## Running Integration Tests

Integration tests are executed using a [Postman/Newman](https://www.npmjs.com/package/newman) collection that validates the RealWorld API spec.

### Prerequisites

- [Docker](https://www.docker.com/) (Newman runs inside a Docker container)
- The API must be running and accessible

### Running the Tests

1. Make sure the application is running (either locally or via Docker Compose):

```bash
docker compose up -d --build
```

2. Run the integration tests against the local API:

```bash
APIURL=http://localhost:8000/api ./postman/run-api-tests.sh
```

The test script accepts the following environment variables:

| Variable | Description | Default |
|---|---|---|
| `APIURL` | Base URL of the API | `https://api.realworld.io/api` |
| `USERNAME` | Test username | Auto-generated based on timestamp |
| `EMAIL` | Test user email | `<USERNAME>@mail.com` |
| `PASSWORD` | Test user password | `password` |

## Resources

* [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
* [OpenTelemetry Python Github](https://github.com/open-telemetry/opentelemetry-python)
* [OpenTelemetry Python Contrib Github](https://github.com/open-telemetry/opentelemetry-python-contrib)
* [OpenTelemetry Demo Project](https://opentelemetry.io/docs/demo/)
* [OpenTelemetry Demo Project Github](https://github.com/open-telemetry/opentelemetry-demo)

<!-- Links -->

[Poetry]: https://python-poetry.org/
[Poetry installation]: https://python-poetry.org/docs/#installation
[Uvicorn]: https://www.uvicorn.org/