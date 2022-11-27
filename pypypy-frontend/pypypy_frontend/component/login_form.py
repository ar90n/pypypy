from typing import TypeVar, Generic, Callable, Any
from dataclasses import dataclass

from alfort.vdom import VDom, el
from alfort_dom.event import handler

Msg = TypeVar("Msg")


@dataclass(frozen=True)
class Props(Generic[Msg]):
    name: str
    on_input: Callable[[str], Msg]
    on_login: Callable[[], Msg]


def login_form(props: Props[Msg]) -> VDom:
    @handler()
    def on_input(event: Any) -> Msg:
        return props.on_input(event.target.value)

    @handler()
    def on_click(_: Any) -> Msg:
        return props.on_login()

    return el(
        "aside",
        {},
        [
            el("label", {}, ["Name"]),
            el(
                "input",
                {
                    "type": "text",
                    "placeholder": "name",
                    "value": props.name,
                    "oninput": on_input,
                },
            ),
            el(
                "button",
                {
                    "style": {"width": "100%"},
                    "onclick": on_click,
                },
                ["Enter"],
            ),
        ],
    )
