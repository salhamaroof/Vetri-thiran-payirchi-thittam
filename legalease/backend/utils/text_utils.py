from __future__ import annotations

import html


def sanitize_text(text: str) -> str:

    replacements = {

        "\u2018": "'",
        "\u2019": "'",

        "\u201c": '"',
        "\u201d": '"',

        "\u2013": "-",
        "\u2014": "-",

        "\u00a0": " ",

        "\u2022": "-",

        "\u200b": "",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    text = "".join(
        char
        for char in text
        if char in "\n\r\t"
        or ord(char) >= 32
    )

    return text.strip()


def escape_html(text: str) -> str:

    return html.escape(
        text,
        quote=True
    )