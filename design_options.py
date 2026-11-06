"""Session-local option management for ClimaForma Increment 5A.

No intervention geometries, energy models, or temperature predictions.
"""
from __future__ import annotations
from copy import deepcopy
from uuid import uuid4

MAX_OPTIONS = 8
MAX_NAME_LENGTH = 64


def _name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError('Option name must be text.')
    value = ' '.join(name.split())
    if not value or len(value) > MAX_NAME_LENGTH:
        raise ValueError(f'Option name must be 1–{MAX_NAME_LENGTH} characters.')
    return value


def new_option(name: str, *, identifier: str | None = None) -> dict:
    return {'id': identifier or uuid4().hex, 'name': _name(name), 'interventions': []}


def _unique_name(options: list[dict], name: str, *, exclude_id: str | None = None) -> str:
    value = _name(name)
    if any(x['name'].casefold() == value.casefold() and x['id'] != exclude_id for x in options):
        raise ValueError('An option with this name already exists.')
    return value


def add_option(options: list[dict], name: str) -> tuple[list[dict], str]:
    if len(options) >= MAX_OPTIONS:
        raise ValueError(f'Maximum {MAX_OPTIONS} design options per site.')
    value = _unique_name(options, name)
    option = new_option(value)
    return [*deepcopy(options), option], option['id']


def rename_option(options: list[dict], option_id: str, name: str) -> list[dict]:
    value = _unique_name(options, name, exclude_id=option_id)
    result = deepcopy(options)
    for option in result:
        if option['id'] == option_id:
            option['name'] = value
            return result
    raise ValueError('Selected design option no longer exists.')


def duplicate_option(options: list[dict], option_id: str) -> tuple[list[dict], str]:
    if len(options) >= MAX_OPTIONS:
        raise ValueError(f'Maximum {MAX_OPTIONS} design options per site.')
    source = next((x for x in options if x['id'] == option_id), None)
    if source is None:
        raise ValueError('Selected design option no longer exists.')
    base = source['name']
    n = 1
    while True:
        suffix = ' — Copy' if n == 1 else f' — Copy {n}'
        proposal = base[:MAX_NAME_LENGTH - len(suffix)] + suffix
        try:
            name = _unique_name(options, proposal)
            break
        except ValueError:
            n += 1
    copy = deepcopy(source)
    copy['id'] = uuid4().hex
    copy['name'] = name
    return [*deepcopy(options), copy], copy['id']


def delete_option(options: list[dict], option_id: str) -> tuple[list[dict], str | None]:
    if not any(x['id'] == option_id for x in options):
        raise ValueError('Selected design option no longer exists.')
    result = [deepcopy(x) for x in options if x['id'] != option_id]
    return result, result[0]['id'] if result else None
