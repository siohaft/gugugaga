# Gugugaga

<p align="center">
  <!-- <img src="icon-raw.png" width="128" alt="Gugu"> -->
  <!-- <img src="icon-raw.png" alt="Gugu"> -->
  <img src="https://github.com/siohaft/gugugaga/blob/main/icon-raw.png?raw=true" alt="Gugu">
</p>

VS Code support for the [**Gugu programming language**](https://github.com/siohaft/gugugaga).

Write, run, and work with `.gugu` files directly in Visual Studio Code.

## Features

- **Syntax highlighting** for Gugu keywords, built-ins, types, strings, comments, numbers, and decorators
- **Gugu file support** with automatic recognition of `.gugu` files
- **Run Gugu files** directly from the editor
- **Gugu file icons**
- **Comment toggling** with `Ctrl + /`
- Support for Gugu's custom decorators and language syntax
- Lightweight and focused on the Gugu language

## Getting Started

### **IMPORTANT**
Gugugaga is a VS Code extension for the Gugu programming language; it does not include the Gugu language itself. 

Please install Gugu before using this extension. You can install Gugu from PyPI with 
```python
python -m pip install gugugaga.
```
### About Extension
Install the extension from the Visual Studio Marketplace, then open any `.gugu` file.

Example:

```gugu
gugu hello(name):
    gu(f"Hello, {name}!")

gua name = gug("What's your name? ")
hello(name)
```

## Running a Gugu File

Open a `.gugu` file and use the **Run Gugu File** button in the editor.

The extension uses the `gugu` command to execute the current file.

Make sure Gugu is installed before running a program:

```bash
python -m pip install gugugaga
```

Then verify the installation:

```bash
gugu --help
```

## Comments

Gugu uses `#` for line comments.

You can toggle comments using:

```text
Ctrl + /
```

Example:

```gugu
# This is a comment
gu("Hello!")
```

## Syntax Highlighting

The extension highlights Gugu's main language elements, including:

- Keywords
- Built-in functions
- Data types
- Decorators
- Strings
- Numbers
- Comments
- Function definitions

## Gugu Decorators

The extension recognizes Gugu's built-in decorators:

```gugu
@gugustatic
@guguclass
@guguproperty
```

## Development

To work on the extension locally, clone the Gugu repository and open the extension directory:

```bash
git clone https://github.com/siohaft/gugugaga.git
cd gugugaga/vscode/gugugaga
code .
```

Press `F5` in VS Code to launch the Extension Development Host.

## Requirements

- Visual Studio Code 1.90 or newer
- Python 3.10 or newer
- Gugu installed and available as the `gugu` command

## Gugu

Learn more about the Gugu programming language in the main project repository:

https://github.com/siohaft/gugugaga

## License

See the main Gugu repository for license information.
