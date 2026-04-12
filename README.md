# ![RealWorld Example App](etc/images/logo.png)

> ### FastAPI codebase containing real world examples (CRUD, auth, advanced patterns, monitoring, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.

This codebase was created to demonstrate a fully fledged backend application built with [**FastAPI**] including CRUD operations, authentication, routing, pagination, and more.

## Description

This project is a Python-based API that uses [**PostgreSQL**] as its database. It is built with [**FastAPI**], a modern, fast (high-performance), web framework for building APIs with Python 3 based on standard Python type hints. The application is fully containerized using [**Docker**], ensuring consistency across development and deployment environments. Additionally, the project integrates [**GitHub Actions**] to automate code style checks, testing, and the building and publishing of Docker images to Docker Hub.

```mermaid
sequenceDiagram
    participant User
    participant Conduit Backend
    participant PostgreSQL
    participant Otel Collector
    participant Jaeger
    participant OpenSearch
    participant Prometheus
    participant Grafana

    User->>Conduit Backend: Requests
    Conduit Backend->>PostgreSQL: Interacts with database
    Conduit Backend->>User: Responses
    Conduit Backend->>Otel Collector: Exposes metrics, traces, and logs
    Otel Collector->>Jaeger: Stores traces
    Otel Collector->>OpenSearch: Stores logs
    Otel Collector->>Prometheus: Stores metrics
    Jaeger->>Grafana: Provides traces
    OpenSearch->>Grafana: Provides logs
    Prometheus->>Grafana: Provides metrics
    Grafana->>User: Displays monitoring dashboard
```

### Techs, tools and services

- [**Python**]: Programming language used to build the backend application.
  - [**FastAPI**]: High-performance web framework for building APIs  with Python based on standard Python type hints.
  - [**SQLModel**]: Package for SQL databases in Python, designed for simplicity, compatibility, and robustness.
  - [**SQLAlchemy**]: Python SQL toolkit and Object Relational Mapper (ORM) that gives application developers the full power and flexibility of SQL.
  - [**Alembic**]: Lightweight database migration tool.
  - [**Poetry**]: Dependency management and packaging tool for Python projects, ensuring reproducible environments.
- [**PostgreSQL**]: Open-source relational database used to store application data.
- [**OpenTelemetry**]: Observability framework for collecting metrics, logs, and traces.
  - [**OpenTelemetry FastAPI Instrumentation**]: Automatically captures traces and metrics from FastAPI endpoints.
  - [**OpenTelemetry SQLAlchemy Instrumentation**]: Tracks database queries.
  - [**OpenTelemetry Logging Instrumentation**]: Integrates application logs into the observability pipeline.
  - [**OpenTelemetry Collector**]: Central service that receives, processes, and exports telemetry data.
- [**Jaeger**]: Distributed tracing system used to visualize and analyze request flows.
- [**Prometheus**]: Monitoring system that collects and stores time-series metrics.
- [**OpenSearch**]: Search and analytics engine used for storing and querying logs.
- [**Grafana**]: Visualization platform for building dashboards from metrics, logs, and traces.
- [**Docker**]: Containerization platform for packaging and running applications consistently.
  - [**Chainguard**]: Secure container images focused on minimal attack surface and supply chain security.
  - [**Distroless**]: Minimal container images containing only the application and its runtime dependencies.
- [**Github Actions**]: CI/CD platform for automating build, test, and deployment workflows.
- [**DependaBot**]: Automatically updates project dependencies to keep them secure and up to date.
- **Pre-commit**: Framework for running automated checks (linting, formatting, etc.) before code commits.

## How it works

The application follows a layered architecture built with [**FastAPI**]:

- **API layer** (`conduit/api/routes/`) — FastAPI routers handling HTTP requests for users, articles, and profiles.
- **Service layer** (`conduit/services/`) — Database operations and other services.
- **Models layer** (`conduit/models.py`) — Models defining the database schema.
- **Schemas layer** (`conduit/schemas/`) — Pydantic models for request/response validation.
- **Core layer** (`conduit/core/`) — Configuration, database engine, and security utilities.

The OpenTelemetry collector is configured in [otel-collector.yml](./etc/shared/otel-collector.yml), alternative exporters can be configured here.

```mermaid
graph TB
subgraph tdf[Telemetry Data Flow]
    subgraph subgraph_padding [ ]
        style subgraph_padding fill:none,stroke:none;
        %% padding to stop the titles clashing
        subgraph od[Conduit]
        ms(FastAPI Backend)
        end

        ms -.->|"OTLP<br/>gRPC"| oc-grpc

        subgraph oc[OTel Collector]
            style oc fill:#97aef3,color:black;
            oc-grpc[/"OTLP Receiver<br/>listening on<br/>grpc://localhost:4317"/]
            oc-proc(Processors)
            oc-spanmetrics[/"Span Metrics Connector"/]
            oc-prom[/"OTLP HTTP Exporter"/]
            oc-otlp[/"OTLP Exporter"/]
            oc-opensearch[/"OpenSearch Exporter"/]

            oc-grpc --> oc-proc

            oc-proc --> oc-prom
            oc-proc --> oc-otlp
            oc-proc --> oc-opensearch
            oc-proc --> oc-spanmetrics
            oc-spanmetrics --> oc-prom

        end

        oc-prom -->|"localhost:9090/api/v1/otlp"| pr-sc
        oc-otlp -->|gRPC| ja-col
        oc-opensearch -->|HTTP| os-http

        subgraph pr[Prometheus]
            style pr fill:#e75128,color:black;
            pr-sc[/"Prometheus OTLP Write Receiver"/]
            pr-tsdb[(Prometheus TSDB)]
            pr-http[/"Prometheus HTTP<br/>listening on<br/>localhost:9090"/]

            pr-sc --> pr-tsdb
            pr-tsdb --> pr-http
        end

        pr-b{{"Browser<br/>Prometheus UI"}}
        pr-http ---->|"localhost:9090/graph"| pr-b

        subgraph ja[Jaeger]
            style ja fill:#60d0e4,color:black;
            ja-col[/"Jaeger Collector<br/>listening on<br/>grpc://jaeger:4317"/]
            ja-db[(Jaeger DB)]
            ja-http[/"Jaeger HTTP<br/>listening on<br/>localhost:16686"/]

            ja-col --> ja-db
            ja-db --> ja-http
        end

        subgraph os[OpenSearch]
            style os fill:#005eb8,color:black;
            os-http[/"OpenSearch<br/>listening on<br/>localhost:9200"/]
            os-db[(OpenSearch Index)]

            os-http ---> os-db
        end

        subgraph gr[Grafana]
            style gr fill:#f8b91e,color:black;
            gr-srv["Grafana Server"]
            gr-http[/"Grafana HTTP<br/>listening on<br/>localhost:3000"/]

            gr-srv --> gr-http
        end

        pr-http --> |"localhost:9090/api"| gr-srv
        ja-http --> |"localhost:16686/api"| gr-srv
        os-http --> |"localhost:9200/api"| gr-srv

        ja-b{{"Browser<br/>Jaeger UI"}}
        ja-http ---->|"localhost:16686/search"| ja-b

        gr-b{{"Browser<br/>Grafana UI"}}
        gr-http -->|"localhost:3000/dashboard"| gr-b
    end
end
```


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
docker compose up -d postgres otel-collector jaeger prometheus grafana opensearch
```

4. Make sure your `.env` file points to the local services (see `.env.example`).

5. Start the application using [Uvicorn]:

```bash
uvicorn conduit.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API docs are served at `http://localhost:8000/docs`.

For full migration documentation, see [`alembic/README.md`](alembic/README.md).

### Running with Docker Compose

The easiest way to run the entire stack (application + infrastructure) is using Docker Compose:

1. Build and start all services:

```bash
docker compose up -d
```

This will start the following services:

| Service | Port | Description |
|---|---|---|
| **conduit-backend** | http://localhost:8000 | FastAPI application |
| **postgres** | localhost:5432 | PostgreSQL database |
| **jaeger** | http://localhost:16686 | Distributed tracing UI |
| **otel-collector** | localhost:4317 | OpenTelemetry Collector |
| **prometheus** | http://localhost:9090 | Metrics storage and querying |
| **grafana** | http://localhost:3000 | Monitoring dashboards |
| **opensearch** | http://localhost:9200 | Log storage and search |

1. To stop all services:

```bash
docker compose down
```

3. To view logs for a specific service:

```bash
docker compose logs -f conduit-backend
```

### Database Migrations (Alembic)

This project uses Alembic to version and apply schema changes.

```bash
poetry run alembic upgrade head
```

## Roadmap

- [x] Pre-commit
- [x] GitHub Actions workflows
- [x] Alembic integrated for database migrations
- [x] Code quality tooling set up (`mypy`, `flake8`, `isort`)
- [x] Pull request and issue templates
- [ ] Write pytest test suite
- [ ] Organize Docker Compose configuration
- [ ] Create Helm package
- [ ] Add security checks with [**Trivy**](https://github.com/aquasecurity/trivy)
- [ ] Create custom grafana dashboard

## Resources

* [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
* [OpenTelemetry Python Github](https://github.com/open-telemetry/opentelemetry-python)
* [OpenTelemetry Python Contrib Github](https://github.com/open-telemetry/opentelemetry-python-contrib)
* [OpenTelemetry Demo Project](https://opentelemetry.io/docs/demo/)
* [OpenTelemetry Demo Project Github](https://github.com/open-telemetry/opentelemetry-demo)

<!-- Links -->

[**Python**]: https://www.python.org/
[**Poetry**]: https://python-poetry.org/
[**FastAPI**]: https://fastapi.tiangolo.com/
[**SQLModel**]: https://sqlmodel.tiangolo.com/
[**SQLAlchemy**]: https://www.sqlalchemy.org/
[**Alembic**]: https://alembic.sqlalchemy.org/en/latest/

[**PostgreSQL**]: https://www.postgresql.org/
[**Jaeger**]: https://www.jaegertracing.io/
[**Prometheus**]: https://prometheus.io/
[**OpenSearch**]: https://opensearch.org/
[**Grafana**]: https://grafana.com/
[**Github Actions**]: https://github.com/features/actions
[**DependaBot**]: https://github.com/dependabot
[**Pre-commit**]: https://pre-commit.com/

[**OpenTelemetry**]: https://opentelemetry.io/
[**OpenTelemetry FastAPI Instrumentation**]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-fastapi
[**OpenTelemetry SQLAlchemy Instrumentation**]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-sqlalchemy
[**OpenTelemetry Logging Instrumentation**]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-logging
[**OpenTelemetry Collector**]: https://opentelemetry.io/docs/collector/

[**Docker**]: https://www.docker.com/
[**Distroless**]: https://github.com/googlecontainertools/distroless
[**Chainguard**]: https://www.chainguard.dev/

[Poetry installation]: https://python-poetry.org/docs/#installation
[Uvicorn]: https://www.uvicorn.org/
