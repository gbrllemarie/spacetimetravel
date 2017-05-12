
![Space Time Travel](/docs/spacetimetravel.png?raw=true "Space Time Travel")

> **SPACETIME TRAVEL** is an imperative language that deals with problems through a step-by-step process that is completed through time and space (memory). The developers got inspired by the parallelization of the concepts of a programming language and time wherein problems are solved in the present—the gap between the past and the future.

> The lexical analyzer that will be used is a Python module called Plex. After the lexical analysis, the tokens produced will be passed into the syntax analyzer implemented by the use of classes which contains the grammar of our language.

## Usage

### Syntax

### Compilation

`main.py` does the actual converting of `.spacetime` code into `.c`.

`spacetime.py` is just a helper that executes whatever appropriate C compiler command needs to be executed.

### Debugging

## Development

> Note: Things that need to be done are commented as `TODOs`.

### Requirements

- Python 2.7
- pip
- (optional) and editor with EditorConfig support

### Setup

1. navigate to the source directory

`cd ./src/`

2. install dependencies

`pip install -r requirements.txt`

3. try converting the included sample file to C (doesn't work yet of course)

`python main.py samples/leapyears.spacetime`

