import json
import types
import typing
from copy import deepcopy
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Literal, Optional, get_args, get_origin, get_type_hints

from .exceptions import StructuredValidationError


class _UnsupportedNativeSchema(ValueError):
    pass


def _schema_for_type(annotation: Any) -> dict[str, Any]:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (typing.Union, types.UnionType):
        return {"anyOf": [_schema_for_type(option) for option in args]}
    if origin is Literal:
        values = list(args)
        literal_types = {
            str: "string",
            bool: "boolean",
            int: "integer",
            float: "number",
            type(None): "null",
        }
        value_type = literal_types.get(type(values[0]), "string") if values else "string"
        return {"type": value_type, "enum": values}
    if origin in (list, tuple, set):
        item_type = args[0] if args else Any
        return {"type": "array", "items": _schema_for_type(item_type)}
    if origin is dict:
        value_type = args[1] if len(args) > 1 else Any
        return {"type": "object", "additionalProperties": _schema_for_type(value_type)}
    if annotation is Any:
        return {}
    if annotation is str:
        return {"type": "string"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is type(None):
        return {"type": "null"}
    if is_dataclass(annotation):
        return json_schema_for_model(annotation) or {}
    if hasattr(annotation, "__required_keys__"):
        hints = get_type_hints(annotation)
        properties = {}
        required = []
        required_origins = tuple(
            value
            for value in (
                getattr(typing, "Required", None),
                getattr(typing, "NotRequired", None),
            )
            if value is not None
        )
        for key, hint in hints.items():
            field_origin = get_origin(hint)
            if field_origin in required_origins:
                hint = get_args(hint)[0]
            properties[key] = _schema_for_type(hint)
            if key in annotation.__required_keys__:
                required.append(key)
        return {"type": "object", "properties": properties, "required": required}
    return {}


def json_schema_for_model(model_class: Any) -> Optional[dict[str, Any]]:
    if isinstance(model_class, dict):
        return deepcopy(model_class)
    if hasattr(model_class, "model_json_schema"):
        return deepcopy(model_class.model_json_schema())
    if hasattr(model_class, "schema"):
        return deepcopy(model_class.schema())
    if is_dataclass(model_class):
        hints = get_type_hints(model_class)
        properties = {
            field.name: _schema_for_type(hints.get(field.name, Any))
            for field in fields(model_class)
        }
        required = [
            field.name
            for field in fields(model_class)
            if field.default is MISSING and field.default_factory is MISSING
        ]
        return {"type": "object", "properties": properties, "required": required}
    if hasattr(model_class, "__required_keys__"):
        return _schema_for_type(model_class)
    return None


def _is_nullable(schema: dict[str, Any]) -> bool:
    schema_type = schema.get("type")
    if isinstance(schema_type, list) and "null" in schema_type:
        return True
    return any(
        branch.get("type") == "null"
        for key in ("anyOf", "oneOf")
        for branch in schema.get(key, [])
        if isinstance(branch, dict)
    )


def _make_nullable(schema: dict[str, Any]) -> dict[str, Any]:
    if _is_nullable(schema):
        return schema
    return {"anyOf": [schema, {"type": "null"}]}


def _normalize_strict_schema(schema: dict[str, Any]) -> None:
    for key in ("$defs", "definitions"):
        definitions = schema.get(key)
        if isinstance(definitions, dict):
            for definition in definitions.values():
                if isinstance(definition, dict):
                    _normalize_strict_schema(definition)
    for key in ("items", "not"):
        child = schema.get(key)
        if isinstance(child, dict):
            _normalize_strict_schema(child)
    for key in ("allOf", "anyOf", "oneOf"):
        branches = schema.get(key)
        if isinstance(branches, list):
            for branch in branches:
                if isinstance(branch, dict):
                    _normalize_strict_schema(branch)

    properties = schema.get("properties")
    if isinstance(properties, dict):
        if schema.get("additionalProperties") not in (None, False):
            raise _UnsupportedNativeSchema("Strict output schemas cannot allow additional properties.")
        original_required = set(schema.get("required", []))
        for name, child in properties.items():
            if not isinstance(child, dict):
                raise _UnsupportedNativeSchema("Schema properties must be JSON Schema objects.")
            _normalize_strict_schema(child)
            if name not in original_required:
                properties[name] = _make_nullable(child)
        schema["required"] = list(properties)
        schema["additionalProperties"] = False
    elif schema.get("type") == "object":
        if schema.get("additionalProperties") not in (None, False):
            raise _UnsupportedNativeSchema("Strict output schemas cannot allow additional properties.")
        schema["additionalProperties"] = False


def strict_json_schema(model_class: Any) -> Optional[dict[str, Any]]:
    """Return a strict JSON Schema for supported response models."""
    schema = json_schema_for_model(model_class)
    if schema is None or schema.get("type") != "object":
        return None
    schema = deepcopy(schema)
    try:
        _normalize_strict_schema(schema)
    except _UnsupportedNativeSchema:
        return None
    return schema


def structured_output_name(model_class: Any) -> str:
    """Make a stable schema name accepted by OpenAI-compatible APIs."""
    if isinstance(model_class, dict):
        name = model_class.get("title", "response")
    else:
        name = getattr(model_class, "__name__", "response")
    name = "".join(char if char.isalnum() or char in "_-" else "_" for char in name)
    return name[:64] or "response"


def is_unsupported_response_schema_error(error: Exception) -> bool:
    """Only allow explicit schema-support errors from client request status codes."""
    status_code = getattr(error, "status_code", None)
    if status_code is None:
        status_code = getattr(getattr(error, "response", None), "status_code", None)
    if status_code not in (400, 422):
        return False

    message = str(error).casefold().replace("-", "_")
    unsupported = (
        "unsupported",
        "not supported",
        "does not support",
        "isn't supported",
        "is not supported",
    )
    mentions_schema = any(
        token in message
        for token in (
            "response_format",
            "response format",
            "json_schema",
            "json schema",
            "output_config",
            "structured output",
            "structured_output",
            "schema",
        )
    )
    return mentions_schema and any(token in message for token in unsupported)


def call_with_schema_fallback(call, native_kwargs: dict[str, Any], fallback_kwargs: dict[str, Any]):
    try:
        return call(**native_kwargs)
    except Exception as error:
        if not is_unsupported_response_schema_error(error):
            raise
    return call(**fallback_kwargs)


async def call_with_schema_fallback_async(
    call, native_kwargs: dict[str, Any], fallback_kwargs: dict[str, Any]
):
    try:
        return await call(**native_kwargs)
    except Exception as error:
        if not is_unsupported_response_schema_error(error):
            raise
    return await call(**fallback_kwargs)


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
        try:
            return model_class.model_validate(data)
        except Exception as error:
            raise StructuredValidationError(f"Structured response validation failed: {error}") from error
    if hasattr(model_class, "parse_obj"):
        try:
            return model_class.parse_obj(data)
        except Exception as error:
            raise StructuredValidationError(f"Structured response validation failed: {error}") from error

    raise StructuredValidationError(f"Unsupported response model: {model_class!r}")
