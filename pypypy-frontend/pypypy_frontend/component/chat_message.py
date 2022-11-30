from dataclasses import dataclass

from alfort.vdom import VDom, el


@dataclass(frozen=True)
class Props:
    author: str
    message: str


def chat_message(props: Props) -> VDom:
    return el(
        "aside",
        {"style": {"width": "70%", "overflow": "scroll"}},
        [
            el("h3", {}, [props.author]),
            el("p", {}, [props.message]),
        ],
    )
