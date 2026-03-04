# crashbytes-result

A practical Result type for Python — `Ok`, `Err`, and pattern matching.

## Install

```bash
pip install crashbytes-result
```

## Usage

```python
from crashbytes_result import Ok, Err, Result, safe

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("division by zero")
    return Ok(a / b)

result = divide(10, 3)
match result:
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")

# Or use .match()
msg = result.match(
    ok=lambda v: f"Got {v:.2f}",
    err=lambda e: f"Failed: {e}",
)

# @safe decorator
@safe
def parse_int(s: str) -> int:
    return int(s)

parse_int("42")   # Ok(42)
parse_int("abc")  # Err(ValueError(...))
```

## API

| Method | Ok | Err |
|--------|-----|------|
| `.unwrap()` | Returns value | Raises `UnwrapError` |
| `.unwrap_or(default)` | Returns value | Returns default |
| `.unwrap_err()` | Raises `UnwrapError` | Returns error |
| `.map(fn)` | `Ok(fn(value))` | `self` |
| `.map_err(fn)` | `self` | `Err(fn(error))` |
| `.bind(fn)` | `fn(value)` | `self` |
| `.match(ok, err)` | `ok(value)` | `err(error)` |
| `.is_ok` | `True` | `False` |
| `.is_err` | `False` | `True` |

## License

MIT
