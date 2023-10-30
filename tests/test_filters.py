from dataclasses import asdict, dataclass

import pytest

from litestar import Litestar, get
from litestar.di import Provide
from litestar.handlers import HTTPRouteHandler
from litestar.params import Dependency, Parameter
from litestar.testing import TestClient


@dataclass
class FilterA:
    field: str | None
    value: str | None


@dataclass
class FilterB:
    field: str | None
    value: str | None


@pytest.fixture
def route() -> HTTPRouteHandler:
    @get('')
    async def r(filters: list[FilterA | FilterB] = Dependency(skip_validation=True)) -> list[dict]:
        return [asdict(f) for f in filters]

    return r


# the tests in this suite that fail seem to show that the way the dependency arguments are being merged as well as the
# way the request params are pulled in are not deterministic. even when there's a `query` value set in the `Parameter`
# object, it may pull the query value from either param, not respecting the data that matches the query argument.
#
# for example, i've seen data come through as any of the following throughout subsequent runs of the test suite:
#     [{'field': 'a', 'value': 'b'}, {'field': 'a', 'value': 'b'}]
#     [{'field': 'b', 'value': 'b'}, {'field': 'b', 'value': 'b'}]
#     [{'field': 'b', 'value': 'a'}, {'field': 'b', 'value': 'a'}]
#     [{'field': 'a', 'value': 'a'}, {'field': 'a', 'value': 'a'}]


def test_duplicated_dependency_arguments__only_passing_values__default_field_values(route: HTTPRouteHandler) -> None:
    def provide_filter_a_filter(
        field: str | None = Parameter(default='a', required=False),
        value: str | None = Parameter(query='valueA', default=None, required=False),
    ) -> FilterA:
        return FilterA(field=field, value=value)

    def provide_filter_b_filter(
        field: str | None = Parameter(default='b', required=False),
        value: str | None = Parameter(query='valueB', default=None, required=False),
    ) -> FilterB:
        return FilterB(field=field, value=value)

    def provide_filter_dependencies(filter_a: FilterA, filter_b: FilterB) -> list[FilterA | FilterB]:
        return [filter_a, filter_b]

    app = Litestar(
        route_handlers=[route],
        dependencies={
            'filter_a': Provide(provide_filter_a_filter, sync_to_thread=False),
            'filter_b': Provide(provide_filter_b_filter, sync_to_thread=False),
            'filters': Provide(provide_filter_dependencies, sync_to_thread=False),
        },
    )

    with TestClient(app=app) as client:
        data = client.get('', params={'valueA': 'a', 'valueB': 'b'}).json()

        # these will fail unexpectedly
        assert {'field': 'a', 'value': 'a'} in data
        assert {'field': 'b', 'value': 'b'} in data


def test_duplicated_dependency_arguments__pass_field_and_value__query_argument_for_field_is_set(
    route: HTTPRouteHandler,
) -> None:
    def provide_filter_a_filter(
        field: str | None = Parameter(query='fieldA', default='a', required=False),
        value: str | None = Parameter(query='valueA', default=None, required=False),
    ) -> FilterA:
        return FilterA(field=field, value=value)

    def provide_filter_b_filter(
        field: str | None = Parameter(query='fieldB', default='b', required=False),
        value: str | None = Parameter(query='valueB', default=None, required=False),
    ) -> FilterB:
        return FilterB(field=field, value=value)

    def provide_filter_dependencies(filter_a: FilterA, filter_b: FilterB) -> list[FilterA | FilterB]:
        return [filter_a, filter_b]

    app = Litestar(
        route_handlers=[route],
        dependencies={
            'filter_a': Provide(provide_filter_a_filter, sync_to_thread=False),
            'filter_b': Provide(provide_filter_b_filter, sync_to_thread=False),
            'filters': Provide(provide_filter_dependencies, sync_to_thread=False),
        },
    )

    with TestClient(app=app) as client:
        data = client.get('', params={'fieldA': 'a', 'valueA': 'a', 'fieldB': 'b', 'valueB': 'b'}).json()

        # these will fail unexpectedly
        assert {'field': 'a', 'value': 'a'} in data
        assert {'field': 'b', 'value': 'b'} in data


def test_duplicated_dependency_arguments__pass_field_and_value__query_argument_for_field_is_set__same_filter_type_different_provides(
    route: HTTPRouteHandler,
) -> None:
    def provide_filter_a_filter(
        field: str | None = Parameter(query='fieldA', default='a', required=False),
        value: str | None = Parameter(query='valueA', default=None, required=False),
    ) -> FilterA:
        return FilterA(field=field, value=value)

    def provide_second_filter_a_filter(
        field: str | None = Parameter(query='secondFieldA', default='a', required=False),
        value: str | None = Parameter(query='secondValueA', default=None, required=False),
    ) -> FilterA:
        return FilterA(field=field, value=value)

    def provide_filter_dependencies(filter_a: FilterA, second_filter_a: FilterA) -> list[FilterA | FilterB]:
        return [filter_a, second_filter_a]

    app = Litestar(
        route_handlers=[route],
        dependencies={
            'filter_a': Provide(provide_filter_a_filter, sync_to_thread=False),
            'second_filter_a': Provide(provide_second_filter_a_filter, sync_to_thread=False),
            'filters': Provide(provide_filter_dependencies, sync_to_thread=False),
        },
    )

    with TestClient(app=app) as client:
        data = client.get('', params={'fieldA': 'a', 'valueA': 'a', 'secondFieldA': 'b', 'secondValueA': 'b'}).json()

        # these will fail unexpectedly
        assert {'field': 'a', 'value': 'a'} in data
        assert {'field': 'b', 'value': 'b'} in data


def test_unique_dependency_arguments(route: HTTPRouteHandler) -> None:
    def provide_filter_a_filter(
        field_a: str | None = Parameter(query='fieldA', default='a', required=False),
        value_a: str | None = Parameter(query='valueA', default=None, required=False),
    ) -> FilterA:
        return FilterA(field=field_a, value=value_a)

    def provide_filter_b_filter(
        field_b: str | None = Parameter(query='fieldB', default='b', required=False),
        value_b: str | None = Parameter(query='valueB', default=None, required=False),
    ) -> FilterB:
        return FilterB(field=field_b, value=value_b)

    def provide_filter_dependencies(filter_a: FilterA, filter_b: FilterB) -> list[FilterA | FilterB]:
        return [filter_a, filter_b]

    app = Litestar(
        route_handlers=[route],
        dependencies={
            'filter_a': Provide(provide_filter_a_filter, sync_to_thread=False),
            'filter_b': Provide(provide_filter_b_filter, sync_to_thread=False),
            'filters': Provide(provide_filter_dependencies, sync_to_thread=False),
        },
    )

    with TestClient(app=app) as client:
        data = client.get('', params={'valueA': 'a', 'valueB': 'b'}).json()

        assert {'field': 'a', 'value': 'a'} in data
        assert {'field': 'b', 'value': 'b'} in data

        data = client.get('', params={'fieldA': 'fieldA', 'valueA': 'a', 'fieldB': 'fieldB', 'valueB': 'b'}).json()

        assert {'field': 'fieldA', 'value': 'a'} in data
        assert {'field': 'fieldB', 'value': 'b'} in data
