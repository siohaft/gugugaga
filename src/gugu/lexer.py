KEYWORDS = {
    "gugugaga": "class",
    "gugu": "def",
    "goo": "if",
    "goga": "elif",
    "gaa": "else",
    "guale": "while",
    "guu": "for",
    "gureak": "break",
    "gugugoo": "continue",
    "ga": "in",
    "go": "as",
    "gunot": "not",
    "guand": "and",
    "guor": "or",
    "goat": "True",
    "gusfand": "False",
    "gu": "print",
    "gug": "input",
    "gin": "min",
    "gax": "max",
    "guo": "open",
    "gaga": "return",
    "gagu": "from",
    "guga": "import",
    "gua": "gua",
    # Decorators
    "gugustatic": "staticmethod",
    "guguclass": "classmethod",
    "guguproperty": "property",
    # Data types
    "guint": "int",
    "gufloat": "float",
    "gudouble": "float",
    "gucomplex": "complex",
    "gubool": "bool",
    "gustr": "str",
    "gubytes": "bytes",
    "gubytearray": "bytearray",
    "gumemoryview": "memoryview",
    "gulist": "list",
    "gutuple": "tuple",
    "gudict": "dict",
    "guset": "set",
    "gufrozenset": "frozenset",
}


def translate_line(line):
    result = []
    word = []
    in_string = False
    quote = None
    escaped = False
    i = 0

    def flush_word():
        if word:
            text = "".join(word)

            if in_string:
                result.append(text)
            else:
                result.append(KEYWORDS.get(text, text))

            word.clear()

    while i < len(line):
        char = line[i]

        # f-string
        if (
            not in_string
            and char in ("f", "F")
            and i + 1 < len(line)
            and line[i + 1] in ('"', "'")
        ):
            flush_word()

            f_prefix = char
            quote_char = line[i + 1]

            result.append(f_prefix)
            result.append(quote_char)

            i += 2

            while i < len(line):
                char = line[i]

                if char == "\\":
                    result.append(char)

                    if i + 1 < len(line):
                        result.append(line[i + 1])
                        i += 2
                        continue

                if char == quote_char:
                    result.append(char)
                    i += 1
                    break

                # Start of an f-string expression
                if char == "{" and not (i + 1 < len(line) and line[i + 1] == "{"):
                    depth = 1
                    j = i + 1
                    expression = []

                    while j < len(line) and depth > 0:
                        current = line[j]

                        if current == "{":
                            depth += 1
                        elif current == "}":
                            depth -= 1

                        if depth > 0:
                            expression.append(current)

                        j += 1

                    if depth != 0:
                        result.append("".join(expression))
                        i = j
                        continue

                    expression_text = "".join(expression)

                    # Translate Gugu keywords inside {...}
                    translated_expression = translate_line(expression_text)

                    result.append("{")
                    result.append(translated_expression)
                    result.append("}")

                    i = j
                    continue

                # Escaped literal {{
                if char == "{" and i + 1 < len(line) and line[i + 1] == "{":
                    result.append("{{")
                    i += 2
                    continue

                # Escaped literal }}
                if char == "}" and i + 1 < len(line) and line[i + 1] == "}":
                    result.append("}}")
                    i += 2
                    continue

                result.append(char)
                i += 1

            continue

        if in_string:
            if escaped:
                result.append(char)
                escaped = False
                i += 1
                continue

            if char == "\\":
                result.append(char)
                escaped = True
                i += 1
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

        i += 1

    flush_word()

    return "".join(result)
