import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from conduit.api.routes.user import router as users_router
from conduit.api.routes.article import router as articles_router
from conduit.core.config import SETTINGS
from conduit.core.database import ENGINE, Base

Base.metadata.create_all(bind=ENGINE)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router)
app.include_router(articles_router)

resource = Resource.create(
    attributes={
        "service.name": "medium-backend",
        "service.instance.id": os.uname().nodename,
    },
)
trace.set_tracer_provider(tracer_provider=TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    span_processor=BatchSpanProcessor(
        span_exporter=OTLPSpanExporter(
            endpoint=str(SETTINGS.OTLP_GRPC_ENDPOINT),
            insecure=True,
        ),
    ),
)

provider = MeterProvider(
    resource=resource,
    metric_readers=[
        PeriodicExportingMetricReader(
            exporter=OTLPMetricExporter(
                endpoint=str(SETTINGS.OTLP_GRPC_ENDPOINT),
                insecure=True,
            ),
        ),
    ],
)
set_meter_provider(meter_provider=provider)

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
exporter = OTLPLogExporter(
    endpoint=str(SETTINGS.OTLP_GRPC_ENDPOINT),
    insecure=True,
)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter=exporter))
handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
SQLAlchemyInstrumentor().instrument(engine=ENGINE)
