from typing import Any, Callable, TypeAlias

from js import WebSocket
from pyodide.ffi import create_proxy

Send: TypeAlias = Callable[[str], None]


def connect(
    ws_url: str,
    /,
    *,
    on_open: Callable[[Any, Send], None] | None = None,
    on_message: Callable[[Any, Send], None] | None = None,
    on_close: Callable[[Any], None] | None = None,
):
    socket = WebSocket.new(ws_url)

    def _send(msg: str) -> None:
        socket.send(msg)

    if on_open is not None:
        socket.addEventListener("open", create_proxy(lambda e: on_open(e, _send)))
    if on_message is not None:
        socket.addEventListener("message", create_proxy(lambda e: on_message(e, _send)))
    if on_close is not None:
        socket.addEventListener("close", create_proxy(lambda e: on_close(e, _send)))
