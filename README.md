

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # create and edit with your OpenAI key
```

## Usage

```bash
python run.py
```

Use the GUI to start, pause, or stop the automation. All events are logged to
`quiz_log.db`.

For headless scripting on Windows, the `automation.answer_question` helper can
be wired into a loop that:

## Tests

```bash
pytest
```

## Optimisation Flags

- `Settings.poll_interval` controls screenshot frequency.
- `Watcher.preprocess` uses grayscale + adaptive thresholding for better OCR.
