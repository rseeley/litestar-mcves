"""Minimal Litestar application."""
from __future__ import annotations

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field
from pydash.strings import camel_case

from litestar import Litestar, get

__all__ = ("async_hello_world",)


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        from_attributes=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


class CamelizedBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=camel_case)


class HelloWorld(CamelizedBaseModel):
    some_value: str
    other_value: str = Field(..., alias="otherValueAlias")


@get("/async")
async def async_hello_world() -> HelloWorld:
    """Route Handler that outputs hello world."""
    return HelloWorld(some_value="Hello World", other_value="Hello World")


app = Litestar(
    route_handlers=[async_hello_world],
    type_encoders={_BaseModel: lambda x: x.model_dump(by_alias=True)},
)
