# Basic AI Auto Assistant

A minimal, test-focused project that demonstrates how a desktop quiz helper
could integrate screen capture, OCR and the ChatGPT API.  The real application
would automate reading quiz questions from the screen, querying ChatGPT for an
answer and clicking the corresponding option.

## Setup

Requirements are listed in `requirements.txt`.  Create a virtual environment and
install them with

```bash
pip install -r requirements.txt
```

Some dependencies such as `pyautogui` and `mss` interact with the system GUI.
The unit tests mock these modules so they can run headlessly.

## Configuration

Runtime behaviour is controlled through environment variables:

- `OPENAI_API_KEY` – API key used by the ChatGPT client.
- `POLL_INTERVAL` – interval in seconds between screen polls (default `1.0`).
- `READ_TIMEOUT` – timeout for reading ChatGPT responses (default `20.0`).
- `CLICK_OFFSET` – pixel distance between answer options (default `40`).

## Running tests

All tests are written with `pytest` and can be executed headlessly:

```bash
pytest -q
```

## Contributing

Code should follow PEP 8 guidelines and include type hints.  The project uses
`black`, `flake8` and `mypy` for formatting and linting.  A GitHub Actions
workflow runs these tools along with the test suite for every commit.
