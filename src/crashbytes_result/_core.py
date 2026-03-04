"""Result type for explicit error handling — Ok[T] | Err[E]."""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, NoReturn, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Represents a successful result containing a value."""

    _value: T

    @property
    def value(self) -> T:
        return self._value

    @property
    def is_ok(self) -> bool:
        return True

    @property
    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        """Return the contained value."""
        return self._value

    def unwrap_or(self, default: object) -> T:
        """Return the contained value (ignores default)."""
        return self._value

    def unwrap_err(self) -> NoReturn:
        """Raise because this is Ok, not Err."""
        raise UnwrapError(f"Called unwrap_err on Ok({self._value!r})")

    def map(self, fn: Callable[[T], U]) -> Ok[U]:
        """Apply *fn* to the contained value."""
        return Ok(fn(self._value))

    def map_err(self, fn: Callable[[Any], Any]) -> Ok[T]:
        """No-op for Ok — return self."""
        return self

    def bind(self, fn: Callable[[T], Result[U, Any]]) -> Result[U, Any]:
        """Apply *fn* that returns a Result."""
        return fn(self._value)

    def match(
        self,
        ok: Callable[[T], U],
        err: Callable[[Any], U],
    ) -> U:
        """Pattern match — calls *ok* branch."""
        return ok(self._value)

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    # Support Python 3.10+ structural pattern matching
    __match_args__ = ("_value",)


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Represents a failed result containing an error."""

    _error: E

    @property
    def error(self) -> E:
        return self._error

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def is_err(self) -> bool:
        return True

    def unwrap(self) -> NoReturn:
        """Raise because this is Err."""
        raise UnwrapError(f"Called unwrap on Err({self._error!r})")

    def unwrap_or(self, default: T) -> T:
        """Return *default* because this is Err."""
        return default

    def unwrap_err(self) -> E:
        """Return the contained error."""
        return self._error

    def map(self, fn: Callable[[Any], Any]) -> Err[E]:
        """No-op for Err — return self."""
        return self

    def map_err(self, fn: Callable[[E], F]) -> Err[F]:
        """Apply *fn* to the contained error."""
        return Err(fn(self._error))

    def bind(self, fn: Callable[[Any], Any]) -> Err[E]:
        """No-op for Err — return self."""
        return self

    def match(
        self,
        ok: Callable[[Any], U],
        err: Callable[[E], U],
    ) -> U:
        """Pattern match — calls *err* branch."""
        return err(self._error)

    def __repr__(self) -> str:
        return f"Err({self._error!r})"

    __match_args__ = ("_error",)


Result = Ok[T] | Err[E]
"""Type alias: a value is either ``Ok[T]`` or ``Err[E]``."""


class UnwrapError(Exception):
    """Raised when unwrapping a Result incorrectly."""


def safe(
    *args: Any,
) -> Any:
    """Decorator that wraps a function to return ``Ok`` or ``Err``.

    Usage::

        @safe
        def parse_int(s: str) -> int:
            return int(s)

        @safe(ValueError, KeyError)
        def lookup(data: dict, key: str) -> str:
            return data[key]
    """
    if len(args) == 1 and callable(args[0]) and not (
        isinstance(args[0], type) and issubclass(args[0], BaseException)
    ):
        fn = args[0]

        @functools.wraps(fn)
        def wrapper(*a: Any, **kw: Any) -> Any:
            try:
                return Ok(fn(*a, **kw))
            except Exception as exc:
                return Err(exc)

        return wrapper

    exceptions = tuple(args)
    if not exceptions:
        exceptions = (Exception,)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*a: Any, **kw: Any) -> Any:
            try:
                return Ok(fn(*a, **kw))
            except exceptions as exc:
                return Err(exc)

        return wrapper

    return decorator
