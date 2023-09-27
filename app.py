"""Minimal Litestar application."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import UUID  # noqa: TCH003

from litestar import Litestar, get
from litestar.di import Provide
from litestar.params import Dependency, Parameter

__all__ = ('IdFilter', 'provide_id_filter', 'route')


@dataclass
class IdFilter:
    ids: list[int] | list[str] | list[UUID]


def provide_id_filter(ids: list[int] | list[str] | list[UUID] | None = Parameter(required=False)) -> IdFilter:
    return IdFilter(ids=ids or [])


@get('')
async def route(id_filter: IdFilter = Dependency(skip_validation=True)) -> dict:
    return asdict(id_filter)


app = Litestar(
    route_handlers=[route],
    dependencies={
        'id_filter': Provide(provide_id_filter, sync_to_thread=False),
    },
)
