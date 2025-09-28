# Python Compiler – ASM-01 & ASM-02

This repo contains both assignments:

1. **ASM-01 – Lexer**
   - Two versions: `lexer_regex.py` (regex) and `lexer_noregex.py` (manual).
   - Handles keywords, identifiers, literals, operators, comments, escaped characters, and Unicode.

2. **ASM-02 – Parser**
   - Recursive-descent parser builds AST from tokens.
   - Detects syntax errors like missing identifiers, unexpected tokens, etc.

## Run
```bash
python main_lexer.py examples/example01.src --regex   # Lexer A
python main_lexer.py examples/example01.src --noregex # Lexer B
python main_parser.py examples/example02.src          # Full AST


# Code file structure
python-compiler/
│
├── compiler/                     # our package
│   ├── __init__.py
│   ├── lexer_regex.py            # Lexer A: with regex
│   ├── lexer_noregex.py          # Lexer B: without regex
│   ├── tokens.py                 # Token definitions
│   ├── parser.py                 # Recursive-descent parser (ASM-02)
│   └── utils.py                  # helpers, error reporting
│
├── examples/
│   ├── example01.src             # minimal test
│   └── example02.src             # big test with loops/ifs etc.
│
├── main_lexer.py                 # entry for lexer only
├── main_parser.py                # entry for full compiler (lexer+parser)
├── requirements.txt              # (optional, if using any deps)
├── README.md
└── LICENSE  (optional)
