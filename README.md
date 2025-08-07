# Quiz Automation Starter

This project provides a starting point for an application that watches a quiz,
captures each question, sends it to ChatGPT for an answer, and clicks the
matching option automatically.

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

On first run the helper `RegionSelector` will prompt for the quiz region and the
ChatGPT response area and store the coordinates in `regions.json`. Use the GUI to
start, pause, or resume the watcher thread. All events are logged to
`quiz_log.db`.

For headless scripting the `automation.answer_question_via_chatgpt` helper can
be wired into a loop that:

1. Screenshots the quiz region and copies it to the clipboard.
2. Pastes the image into a ChatGPT window and submits it.
3. Reads the model response by OCRing the ChatGPT output area.
4. Clicks the answer option that matches the returned letter.
5. Aborts without clicking if no valid letter is detected.

## Tests

```bash
pytest
```

## Optimisation Flags

- `Settings.poll_interval` controls screenshot frequency.
- `Watcher.preprocess` uses grayscale + adaptive thresholding for better OCR.
- `Stats.summary()` exposes average OCR and model latencies for tuning.
