"""Tests for crashbytes-result."""

from __future__ import annotations

import pytest

from crashbytes_result import Err, Ok, UnwrapError, safe


class TestOk:
    def test_value(self) -> None:
        assert Ok(42).value == 42

    def test_is_ok(self) -> None:
        assert Ok(1).is_ok is True

    def test_is_err(self) -> None:
        assert Ok(1).is_err is False

    def test_unwrap(self) -> None:
        assert Ok("hello").unwrap() == "hello"

    def test_unwrap_or(self) -> None:
        assert Ok(10).unwrap_or(0) == 10

    def test_unwrap_err_raises(self) -> None:
        with pytest.raises(UnwrapError, match="Called unwrap_err on Ok"):
            Ok(1).unwrap_err()

    def test_map(self) -> None:
        result = Ok(5).map(lambda x: x * 2)
        assert result == Ok(10)

    def test_map_err_is_noop(self) -> None:
        result = Ok(5).map_err(lambda e: str(e))
        assert result == Ok(5)

    def test_bind_ok(self) -> None:
        result = Ok(5).bind(lambda x: Ok(x + 1))
        assert result == Ok(6)

    def test_bind_err(self) -> None:
        result = Ok(5).bind(lambda x: Err("fail"))
        assert result == Err("fail")

    def test_match_ok(self) -> None:
        value = Ok(42).match(ok=lambda v: f"got {v}", err=lambda e: f"err {e}")
        assert value == "got 42"

    def test_repr(self) -> None:
        assert repr(Ok(42)) == "Ok(42)"
        assert repr(Ok("hi")) == "Ok('hi')"

    def test_equality(self) -> None:
        assert Ok(1) == Ok(1)
        assert Ok(1) != Ok(2)
        assert Ok(1) != Err(1)

    def test_frozen(self) -> None:
        with pytest.raises(AttributeError):
            Ok(1)._value = 2  # type: ignore[misc]


class TestErr:
    def test_error(self) -> None:
        assert Err("fail").error == "fail"

    def test_is_ok(self) -> None:
        assert Err("x").is_ok is False

    def test_is_err(self) -> None:
        assert Err("x").is_err is True

    def test_unwrap_raises(self) -> None:
        with pytest.raises(UnwrapError, match="Called unwrap on Err"):
            Err("oops").unwrap()

    def test_unwrap_or(self) -> None:
        assert Err("fail").unwrap_or(42) == 42

    def test_unwrap_err(self) -> None:
        assert Err("fail").unwrap_err() == "fail"

    def test_map_is_noop(self) -> None:
        result = Err("fail").map(lambda x: x * 2)
        assert result == Err("fail")

    def test_map_err(self) -> None:
        result = Err("fail").map_err(lambda e: e.upper())
        assert result == Err("FAIL")

    def test_bind_is_noop(self) -> None:
        result = Err("fail").bind(lambda x: Ok(x + 1))
        assert result == Err("fail")

    def test_match_err(self) -> None:
        value = Err("bad").match(ok=lambda v: f"got {v}", err=lambda e: f"err {e}")
        assert value == "err bad"

    def test_repr(self) -> None:
        assert repr(Err("fail")) == "Err('fail')"

    def test_equality(self) -> None:
        assert Err("a") == Err("a")
        assert Err("a") != Err("b")
        assert Err(1) != Ok(1)

    def test_frozen(self) -> None:
        with pytest.raises(AttributeError):
            Err("x")._error = "y"  # type: ignore[misc]


class TestPatternMatching:
    def test_match_ok(self) -> None:
        result: Ok[int] | Err[str] = Ok(42)
        match result:
            case Ok(value):
                assert value == 42
            case Err(error):
                pytest.fail(f"Unexpected Err: {error}")

    def test_match_err(self) -> None:
        result: Ok[int] | Err[str] = Err("fail")
        match result:
            case Ok(value):
                pytest.fail(f"Unexpected Ok: {value}")
            case Err(error):
                assert error == "fail"


class TestSafeDecorator:
    def test_safe_returns_ok(self) -> None:
        @safe
        def parse(s: str) -> int:
            return int(s)

        result = parse("42")
        assert result == Ok(42)

    def test_safe_returns_err(self) -> None:
        @safe
        def parse(s: str) -> int:
            return int(s)

        result = parse("abc")
        assert isinstance(result, Err)
        assert isinstance(result.error, ValueError)

    def test_safe_with_specific_exceptions(self) -> None:
        @safe(ValueError)
        def parse(s: str) -> int:
            return int(s)

        result = parse("abc")
        assert isinstance(result, Err)

    def test_safe_with_specific_exceptions_unhandled(self) -> None:
        @safe(ValueError)
        def parse(s: str) -> int:
            raise TypeError("wrong type")

        with pytest.raises(TypeError, match="wrong type"):
            parse("abc")

    def test_safe_preserves_name(self) -> None:
        @safe
        def my_func() -> int:
            return 1

        assert my_func.__name__ == "my_func"

    def test_safe_with_kwargs(self) -> None:
        @safe
        def add(a: int, b: int = 0) -> int:
            return a + b

        assert add(1, b=2) == Ok(3)

    def test_safe_no_args_catches_all(self) -> None:
        @safe()
        def boom() -> int:
            raise RuntimeError("boom")

        result = boom()
        assert isinstance(result, Err)
        assert isinstance(result.error, RuntimeError)
