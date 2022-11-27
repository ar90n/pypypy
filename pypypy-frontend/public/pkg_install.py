import micropip  # type: ignore # noqa: F401

try:
    await micropip.install("pypypy_frontend-0.0.1-py3-none-any.whl")  # type: ignore # noqa: F704
except ValueError:
    await micropip.install("../dist/pypypy_frontend-0.0.1-py3-none-any.whl")  # type: ignore # noqa: F704