# WrestleGM

WrestleGM is a single-player, text-based wrestling booking simulation game built with Python and the [Textual](https://textual.textualize.io/) framework.

## Getting Started

### Requirements

-   Python 3.11+
-   [uv](https://github.com/astral-sh/uv) (for environment and dependency management)

### Setup

1.  **Create the virtual environment and install dependencies:**

    ```bash
    uv sync
    ```

### Running the Application

To start the game, run:

```bash
uv run python main.py
```

### Running Tests

To run the full test suite, use pytest:

```bash
uv run pytest
```

To update the UI snapshot tests after making intentional changes, run:

```bash
uv run pytest tests/test_ui_snapshots.py --snapshot-update
```

## Documentation

The project documentation is built with [MkDocs](https://www.mkdocs.org/). To view it locally, run:

```bash
uv run mkdocs serve
```

Then, open your browser to `http://127.0.0.1:8000`.

The documentation is written for a Product Owner audience and explains the application's features, user flow, simulation rules, and architecture.