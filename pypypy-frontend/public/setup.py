import os
import micropip  # type: ignore # noqa: F401

os.environ.update(
    {
        "API_ID": "c84ibhg2yd",
        "REGION": "ap-northeast-1",
        "STAGE": "dev",
    }
)

await micropip.install("../dist/pypypy_frontend-0.0.1-py3-none-any.whl")  # type: ignore # noqa: F704
