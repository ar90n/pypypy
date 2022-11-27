# SPDX-FileCopyrightText: 2022-present Masahiro Wada <argon.argon.argon@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import TypeAlias, Any, Callable, Coroutine
from dataclasses import dataclass, fields

from alfort import Dispatch, Effect
from alfort.vdom import VDom, el
from alfort_dom import AlfortDom

from pypypy_frontend.component.login_form import login_form, Props as LoginFormProps
from pypypy_frontend.component.chat_message import chat_message, Props as ChatMessageProps
from pypypy_frontend.component.chat_form import chat_form, Props as ChatFormProps
from pypypy_frontend.component.header import header


@dataclass(frozen=True)
class AuthedUser:
    name: str


@dataclass(frozen=True)
class NonAuthedUser:
    pass


@dataclass(frozen=True)
class ChatMessage:
    author: str
    body: str


@dataclass(frozen=True)
class State:
    user: AuthedUser | NonAuthedUser
    messages: list[ChatMessage]
    message_input: str
    name_input: str

    def update(self, values: dict[str, Any]) -> "State":
        cur = {field.name: getattr(self, field.name) for field in fields(self)}
        cur.update(values)
        return State(**cur)


@dataclass(frozen=True)
class UpdateName:
    name: str


@dataclass(frozen=True)
class RequestEnterChat:
    ...


@dataclass(frozen=True)
class EnterChat:
    user: AuthedUser


@dataclass(frozen=True)
class UpdateMessage:
    message: str


@dataclass(frozen=True)
class SendMessage:
    ...


@dataclass(frozen=True)
class RecvMessage:
    message: ChatMessage


Msg: TypeAlias = UpdateName | EnterChat | UpdateName | SendMessage | RecvMessage


def init() -> tuple[State, list[Effect[Msg]]]:
    state = State(user=NonAuthedUser(), messages=[], message_input="", name_input="")
    return state, []


def auth_page(state: State) -> VDom:
    props = LoginFormProps[Msg](
        name=state.name_input,
        on_input=lambda s: UpdateName(s),
        on_login=lambda: RequestEnterChat(),
    )
    return el(
        "section",
        {},
        [login_form(props)],
    )


def chat_page(state: State) -> VDom:
    messages = [
        chat_message(ChatMessageProps(author=msg.author, message=msg.body))
        for msg in state.messages
    ]

    return el(
        "section",
        {},
        [
            el(
                "div",
                {
                    "style": {
                        "flex-direction": "column",
                        "justify-content": "center",
                        "align-items": "center",
                        "display": "flex",
                        "width": "100%",
                        "height": "100%",
                    }
                },
                [
                    *messages,
                    chat_form(
                        ChatFormProps(
                            message=state.message_input,
                            on_input=lambda s: UpdateMessage(s),
                            on_send=lambda: SendMessage(),
                        )
                    ),
                ],
            ),
        ],
    )


def view(state: State) -> VDom:
    content = (
        chat_page(state) if isinstance(state.user, AuthedUser) else auth_page(state)
    )
    return el("body", {}, [el("main", {}, [header(), content])])


def create_enter_request_effect(
    name: str,
) -> Callable[[Dispatch[Msg]], Coroutine[None, None, Any]]:
    async def enter_request(dispatch: Dispatch[Msg]) -> None:
        dispatch(EnterChat(user=AuthedUser(name=name)))

    return enter_request


def create_send_request_effect(
    user: AuthedUser,
    message: str,
) -> Callable[[Dispatch[Msg]], Coroutine[None, None, Any]]:
    async def send_request(dispatch: Dispatch[Msg]) -> None:
        dispatch(RecvMessage(message=ChatMessage(author=user.name, body=message)))

    return send_request


def update(msg: Msg, state: State) -> tuple[State, list[Effect[Msg]]]:
    match msg:
        case UpdateName(name):
            return state.update({"name_input": name}), []
        case RequestEnterChat():
            return state, [create_enter_request_effect(name=state.name_input)]
        case EnterChat(user):
            return state.update({"user": user}), []
        case UpdateMessage(message):
            return state.update({"message_input": message}), []
        case SendMessage():
            return state.update({"message_input": ""}), [
                create_send_request_effect(user=state.user, message=state.message_input)
            ]
        case RecvMessage(message):
            return state.update({"messages": [*state.messages, message]}), []


app = AlfortDom[State, Msg](
    init=init,
    view=view,
    update=update,
)
