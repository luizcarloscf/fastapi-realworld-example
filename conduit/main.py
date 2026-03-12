import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace, metrics, _logs
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from conduit.core.config import SETTINGS
from conduit.core.database import ENGINE
from sqlmodel import SQLModel


from conduit.api.routes.user import router as users_router
from conduit.api.routes.article import router as articles_router
from conduit.api.routes.comment import router as comments_router
from conduit.api.routes.profile import router as profiles_router
from conduit.api.routes.tag import router as tags_router


app = FastAPI(
    title="Conduit Backend API",
    description="Backend API for the Conduit application.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router)
app.include_router(articles_router)
app.include_router(comments_router)
app.include_router(profiles_router)
app.include_router(tags_router)


@app.on_event("startup")
async def on_startup():
    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


resource = Resource.create(
    attributes={
        "service.name": "conduit-backend",
        "service.instance.id": os.uname().nodename,
    },
)

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    span_processor=BatchSpanProcessor(
        span_exporter=OTLPSpanExporter(
            endpoint=str(SETTINGS.OTLP_GRPC_ENDPOINT),
            insecure=True,
        ),
    ),
)
trace.set_tracer_provider(tracer_provider=tracer_provider)

meter_provider = MeterProvider(
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
metrics.set_meter_provider(meter_provider=meter_provider)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        exporter=OTLPLogExporter(
            endpoint=str(SETTINGS.OTLP_GRPC_ENDPOINT),
            insecure=True,
        )
    )
)
_logs.set_logger_provider(logger_provider)

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d]"
    " [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s"
    " resource.service.name=%(otelServiceName)s"
    " trace_sampled=%(otelTraceSampled)s] - %(message)s"
)

handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, force=True)
logging.getLogger().addHandler(handler)

# Force uvicorn loggers to propagate to root so the OTel handler exports them
for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    _logger = logging.getLogger(_name)
    _logger.handlers.clear()
    _logger.propagate = True

LoggingInstrumentor().instrument(set_logging_format=True)
FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=tracer_provider,
    meter_provider=meter_provider,
)
SQLAlchemyInstrumentor().instrument(engine=ENGINE.sync_engine)
