# My-Mine

Miner Dungeon RPG - Raids. A pygame game where you mine ores and fight bat raids.

## Running on Desktop

```bash
pip install pygame-ce
python main.py
```

## Running in the Browser (pygbag / WebAssembly)

[pygbag](https://pygame-web.github.io/) compiles the game to WebAssembly via Pyodide so it runs directly in a browser.

### Install pygbag

```bash
pip install pygbag
```

### Build for the web

Run this command from the repository root (the folder containing `main.py`):

```bash
pygbag --build .
```

The generated web build is placed in `build/web/`. Open `build/web/index.html` in a browser, or serve it with any static file server:

```bash
python -m http.server --directory build/web
# then open http://localhost:8000 in your browser
```

### Live preview during development

```bash
pygbag .
# opens http://localhost:8000 automatically
```

### Caveats

- Audio is not used in this game, so there are no audio-related browser restrictions.
- The game requires a browser that supports WebAssembly (all modern browsers do).
- Mobile/touch input is not currently supported.
