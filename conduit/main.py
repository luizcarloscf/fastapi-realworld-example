import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import _logs, metrics, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from conduit.api.routes.article import router as articles_router
from conduit.api.routes.comment import router as comments_router
from conduit.api.routes.health import router as health_router
from conduit.api.routes.profile import router as profiles_router
from conduit.api.routes.tag import router as tags_router
from conduit.api.routes.user import router as users_router
from conduit.core.database import ENGINE
from conduit.core.settings import get_settings_cached
from conduit.exceptions import add_http_exception_handler

settings = get_settings_cached()

app = FastAPI(
    title="Conduit Backend API",
    description="Backend API for the Conduit application.",
    version="0.1.0",
    docs_url="/",
)
add_http_exception_handler(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.allowed_cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(prefix="/api", router=health_router)
app.include_router(prefix="/api", router=users_router)
app.include_router(prefix="/api", router=articles_router)
app.include_router(prefix="/api", router=comments_router)
app.include_router(prefix="/api", router=profiles_router)
app.include_router(prefix="/api", router=tags_router)


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
            endpoint=str(settings.otlp_grpc_endpoint),
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
                endpoint=str(settings.otlp_grpc_endpoint),
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
            endpoint=str(settings.otlp_grpc_endpoint),
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
