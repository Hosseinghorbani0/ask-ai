import json
from dataclasses import fields, is_dataclass
from typing import Any, get_args, get_origin, get_type_hints

from .exceptions import StructuredValidationError


def _validate_dataclass(model_class: type[Any], data: Any) -> Any:
    if not isinstance(data, dict):
        raise StructuredValidationError("Dataclass responses must be JSON objects.")
    hints = get_type_hints(model_class)
    values = {}
    for field in fields(model_class):
        if field.name not in data:
            raise StructuredValidationError(f"Missing dataclass field: {field.name}")
        value = data[field.name]
        expected = hints.get(field.name)
        if expected and not _matches_type(value, expected):
            raise StructuredValidationError(f"Invalid type for dataclass field: {field.name}")
        values[field.name] = value
    return model_class(**values)


def _matches_type(value: Any, expected: Any) -> bool:
    origin = get_origin(expected)
    args = get_args(expected)
    if origin is None:
        return expected is Any or isinstance(value, expected)
    if origin is list:
        return isinstance(value, list) and (not args or all(_matches_type(item, args[0]) for item in value))
    if origin is dict:
        return isinstance(value, dict)
    if origin is tuple:
        return isinstance(value, tuple) or isinstance(value, list)
    if origin is type(None):
        return value is None
    if origin is Any:
        return True
    return any(_matches_type(value, option) for option in args)


def parse_structured(text: str, model_class: Any) -> Any:
    """Parse and validate JSON text against a supported response schema."""
    try:
        data = json.loads(text)
    except (TypeError, json.JSONDecodeError) as error:
        raise StructuredValidationError(f"Structured response is not valid JSON: {error}") from error

    if isinstance(model_class, dict):
        try:
            import jsonschema
        except ImportError as error:
            raise StructuredValidationError(
                "JSON Schema validation requires the 'jsonschema' optional dependency."
            ) from error
        try:
            jsonschema.validate(data, model_class)
        except Exception as error:
            raise StructuredValidationError(f"JSON Schema validation failed: {error}") from error
        return data

    if is_dataclass(model_class):
        return _validate_dataclass(model_class, data)

    if hasattr(model_class, "__required_keys__"):
        hints = get_type_hints(model_class)
        if not isinstance(data, dict):
            raise StructuredValidationError("TypedDict responses must be JSON objects.")
        missing = model_class.__required_keys__ - data.keys()
        if missing:
            raise StructuredValidationError(f"Missing TypedDict fields: {sorted(missing)}")
        for key, expected in hints.items():
            if key in data and not _matches_type(data[key], expected):
                raise StructuredValidationError(f"Invalid type for TypedDict field: {key}")
        return data

    if hasattr(model_class, "model_validate"):
        return model_class.model_validate(data)
    if hasattr(model_class, "parse_obj"):
        return model_class.parse_obj(data)

    raise StructuredValidationError(f"Unsupported response model: {model_class!r}")
