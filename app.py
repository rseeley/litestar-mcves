"""Minimal Litestar application."""
from __future__ import annotations

from typing import Any

from litestar import Litestar, get

__all__ = ('async_hello_world',)


@get('/async')
async def async_hello_world() -> dict[str, Any]:
    """Route Handler that outputs hello world."""
    return {'hello': 'world'}


app = Litestar(
    debug=True,
    route_handlers=[async_hello_world],
)
