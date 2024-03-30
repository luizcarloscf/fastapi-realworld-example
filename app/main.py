from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


from app.core.config import SETTINGS
from app.core.database import Base, ENGINE
from app.api.routes import user

Base.metadata.create_all(bind=ENGINE)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)

resource = Resource.create(
    attributes={
        "service.name": "medium-backend",
        "compose_service": "medium-backend",
    }
)
tracer = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer)
tracer.add_span_processor(
    span_processor=BatchSpanProcessor(
        span_exporter=OTLPSpanExporter(
            endpoint=str(SETTINGS.OTLP_GRPC_ENDPOINT),
        )
    )
)
LoggingInstrumentor().instrument(set_logging_format=True)
FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
SQLAlchemyInstrumentor().instrument(engine=ENGINE)
