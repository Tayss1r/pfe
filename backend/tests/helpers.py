# tests/helpers.py
#Le fichier helpers.py sert à construire automatiquement un JSON valide.Donc tu n’as pas besoin d’écrire chaque champ à la main à chaque test.

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import get_origin, get_args, Union


def _unwrap_optional(tp):
    origin = get_origin(tp)
    if origin is Union:
        args = [a for a in get_args(tp) if a is not type(None)]
        return args[0] if args else str
    return tp


def _guess_value(field_name: str, annotation):
    name = field_name.lower()
    annotation = _unwrap_optional(annotation)

    if "email" in name:
        return "test.user@example.com"
    if "password" in name:
        return "Str0ngP@ssw0rd!"
    if name.endswith("code") or "code" in name:
        return "123456"
    if "token" in name:
        return "dummy-token"
    if "client" in name:
        return "web"

    origin = get_origin(annotation)
    if origin in (list, set, tuple):
        return []
    if origin is dict:
        return {}

    if annotation in (str,):
        return "test"
    if annotation in (int,):
        return 1
    if annotation in (bool,):
        return True
    if annotation in (datetime,):
        return datetime.now().isoformat()

    try:
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return list(annotation)[0].value
    except Exception:
        pass

    try:
        if getattr(annotation, "__name__", "") == "UUID":
            return str(uuid4())
    except Exception:
        pass

    return "test"


def make_payload(model_cls, overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    payload = {}

    if hasattr(model_cls, "model_fields"):  # Pydantic v2
        for fname, finfo in model_cls.model_fields.items():
            required = finfo.is_required() if hasattr(finfo, "is_required") else False
            if not required:
                continue
            payload[fname] = overrides.get(fname, _guess_value(fname, getattr(finfo, "annotation", str)))

    elif hasattr(model_cls, "__fields__"):  # Pydantic v1
        for fname, finfo in model_cls.__fields__.items():
            if not finfo.required:
                continue
            payload[fname] = overrides.get(fname, _guess_value(fname, getattr(finfo, "outer_type_", str)))

    payload.update(overrides)
    return payload