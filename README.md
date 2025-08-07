# Quiz Automation Starter

This project provides a starting point for an application that watches a quiz,
extracts the question with OCR, uses a lightweight local model to pick an
answer, and automatically clicks the matching option.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # optional: adjust poll interval
```

## Usage

```bash
python run.py
```

Use the GUI to start, pause, or stop the automation. All events are logged to
`quiz_log.db`.

For headless scripting the `automation.answer_question` helper can be wired into
a loop that:

1. Screenshots the quiz region.
2. Runs OCR and asks the local heuristic model for the best option.
3. Clicks the answer option that matches the returned letter.

## Tests

```bash
pytest
```

## Optimisation Flags

- `Settings.poll_interval` controls screenshot frequency.
- `Watcher.preprocess` uses grayscale + adaptive thresholding for better OCR.
- `Stats.summary()` exposes average OCR and model latencies for tuning.
