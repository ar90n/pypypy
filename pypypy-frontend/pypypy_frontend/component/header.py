from alfort.vdom import VDom, el


def header() -> VDom:
    return el(
        "header",
        {},
        [
            el("h1", {}, ["PyPyPy - Simple Chat App by Python"]),
            el(
                "span",
                {},
                [
                    el(
                        "a",
                        {"href": "https://github.com/ar90n/pypypy"},
                        ["ar90n/pypypy"],
                    ),
                ],
            ),
        ],
    )
