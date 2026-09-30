KEYWORDS = {
    "gugugaga": "class",
    "gugu": "def",
    "goo": "if",
    "gaa": "else",
    "guu": "for",
    "ga": "in",
    "go": "as",
    "gu": "print",
    "gug": "input",
    "gaga": "return",
    "gagu": "from",
    "guga": "import",
    "gua": "gua",
}


def translate_line(line):
    result = []
    word = []
    in_string = False
    quote = None
    escaped = False

    def flush_word():
        if word:
            text = "".join(word)

            if in_string:
                result.append(text)
            else:
                result.append(KEYWORDS.get(text, text))

            word.clear()

    for char in line:
        if in_string:
            if escaped:
                word.append(char)
                escaped = False
                continue

            if char == "\\":
                word.append(char)
                escaped = True
                continue

            if char == quote:
                flush_word()
                in_string = False
                quote = None
                result.append(char)
            else:
                word.append(char)

        else:
            if char in ('"', "'"):
                flush_word()
                in_string = True
                quote = char
                result.append(char)

            elif char.isalnum() or char == "_":
                word.append(char)

            else:
                flush_word()
                result.append(char)

    flush_word()

    return "".join(result)
