from collections.abc import Iterable, Iterator, MutableSet
from typing import Annotated, TypeVar

from pydantic import BeforeValidator, PlainSerializer

T = TypeVar("T")


class OrderedSet(MutableSet[T]):
    """A set that preserves insertion order by internally using a dict."""

    def __init__(self, iterable: Iterable[T] = []):
        self._d = dict.fromkeys(iterable)

    def add(self, value: T) -> None:
        self._d[value] = None

    def discard(self, value: T) -> None:
        self._d.pop(value, None)

    def update(self, iterable: Iterable[T]) -> None:
        self._d.update(dict.fromkeys(iterable))

    @property
    def first(self) -> T:
        return next(iter(self))

    @property
    def last(self) -> T:
        *_, last = iter(self)
        return last

    def __contains__(self, x: object) -> bool:
        return self._d.__contains__(x)

    def __len__(self) -> int:
        return self._d.__len__()

    def __iter__(self) -> Iterator[T]:
        return self._d.__iter__()

    def __str__(self):
        return f"{{{', '.join(str(i) for i in self)}}}"

    def __repr__(self):
        return f"<OrderedSet {self}>"

    def union(self, other: "OrderedSet[T]") -> "OrderedSet[T]":
        result = OrderedSet(self)
        result.update(other)
        return result
        
    def difference(self, other: Iterable[T]) -> "OrderedSet[T]":
        """Return a new OrderedSet with elements in this set but not in other."""
        result = OrderedSet(self)
        for item in other:
            result.discard(item)
        return result


OrderedSetAnnotated = Annotated[
    OrderedSet[T],
    BeforeValidator(lambda arr: OrderedSet(arr)),  # Ensure input is a numpy array
    PlainSerializer(lambda ordered_set: list(ordered_set), return_type=list),
]
