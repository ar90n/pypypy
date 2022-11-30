from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from alfort.vdom import VDom, el
from alfort_dom.event import handler

Msg = TypeVar("Msg")


@dataclass(frozen=True)
class Props(Generic[Msg]):
    message: str
    on_input: Callable[[str], Msg]
    on_send: Callable[[], Msg]


def chat_form(props: Props[Msg]) -> VDom:
    @handler()
    def on_input(event: Any) -> Msg:
        return props.on_input(event.target.value)

    @handler()
    def on_click(_: Any) -> Msg:
        return props.on_send()

    return el(
        "aside",
        {"style": {"width": "70%"}},
        [
            el(
                "input",
                {
                    "type": "text",
                    "style": {"max-width": "100%"},
                    "placeholder": "message",
                    "value": props.message,
                    "oninput": on_input,
                },
            ),
            el(
                "button",
                {"style": {"width": "100%"}, "onclick": on_click},
                ["Send"],
            ),
        ],
    )
