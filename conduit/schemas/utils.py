from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import PlainSerializer, ValidatorFunctionWrapHandler


def check_not_none_if_set(
    value: Any,
    handler: ValidatorFunctionWrapHandler,
) -> Any:
    if value is None:
        raise ValueError("can't be blank")
    if isinstance(value, str) and len(value.strip()) == 0:
        raise ValueError("can't be blank")
    return handler(value)


def normalize_to_none(
    value: Any,
    handler: ValidatorFunctionWrapHandler,
) -> Any:
    if isinstance(value, str) and len(value.strip()) == 0:
        value = None
    return handler(value)


DatetimeISOFormat = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: dt.replace(tzinfo=timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z"),
        return_type=str,
        when_used="json",
    ),
]
