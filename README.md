# Quiz Automation

## Overview
The `quiz_automation` package demonstrates how to automate multiple‑choice quizzes by controlling the ChatGPT web interface.  Screenshots of the question are pasted into ChatGPT, the model's response is OCR'd, and the chosen option is clicked on screen.  Heavy desktop automation dependencies are optional and replaced with light stand‑ins when unavailable.

Core modules provide:
- high level helpers to paste images, read responses, and click answers
- a threaded runner that repeatedly captures questions, asks ChatGPT, and records metrics
- a PySide6 GUI that displays live statistics
- utilities for monitoring new questions, selecting screen regions, and simple CV heuristics



An example `.env` file:

```dotenv
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=o4-mini-high
# OPENAI_SYSTEM_PROMPT="Reply with JSON {'answer':'A|B|C|D'}"
# POLL_INTERVAL=1.0
# TEMPERATURE=0.0
# OCR_BACKEND=tesseract
# QUIZ_REGION=[100,100,600,400]
# CHAT_BOX=[800,900]
# RESPONSE_REGION=[100,550,600,150]
# OPTION_BASE=[100,520]
```

Copy `.env.example` to `.env` and adjust values as needed. Key options:

| Key | Description |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API key used for completions |
| `OPENAI_MODEL` | Model name to query (default `o4-mini-high`) |
| `OPENAI_SYSTEM_PROMPT` | System prompt sent before each question |
| `POLL_INTERVAL` | Seconds to wait before scanning for the next question |
| `TEMPERATURE` | Sampling temperature for the model |
| `OCR_BACKEND` | OCR engine to use, e.g. `tesseract` |
| `QUIZ_REGION` | `[x,y,w,h]` rectangle containing the quiz question |
| `CHAT_BOX` | `[x,y]` coordinates of the ChatGPT input box |
| `RESPONSE_REGION` | `[x,y,w,h]` region to OCR ChatGPT's answer |
| `OPTION_BASE` | `[x,y]` origin for the answer choices |


## `quiz-automation` command
The package installs a `quiz-automation` script that wraps the command‑line interface in `run.py`.

### Optional dependencies
Running the command in a headless environment only needs `pydantic`, `pydantic-settings`, and `mss`. Installing the extras enables full desktop automation:

* `pyautogui` – screen control and screenshots
* `pytesseract` – OCR for ChatGPT's responses
* `opencv-python` – computer‑vision helpers
* `PySide6` – GUI for live statistics
* `numpy` – array helpers for CV routines



```bash
sudo apt-get install tesseract-ocr
```

### Running
1. Install the project:
   ```bash
   pip install -e .
   ```
   Include the `[full]` extras to enable GUI automation and OCR.
2. Copy `.env.example` to `.env` and fill in the configuration values.
3. Invoke the script with a mode flag. Optional arguments control the backend,
   question limit, logging, and configuration loading:




## CLI example
```python
from quiz_automation import answer_question, Stats
from quiz_automation.config import Settings
import pyautogui

cfg = Settings()
options = list("ABCD")

img = pyautogui.screenshot(cfg.quiz_region)
letter = answer_question(
    img,
    cfg.chat_box,
    cfg.response_region,
    options,
    cfg.option_base,
    stats=Stats(),
)
print(f"Model chose {letter}")
```
This snippet grabs the current question, asks ChatGPT for help, and clicks the selected answer.  Adjust the coordinates to match your screen layout.

## GUI example
```python
from quiz_automation import QuizGUI, QuizRunner
from quiz_automation.config import Settings

cfg = Settings()
options = list("ABCD")

ui = QuizGUI()
runner = QuizRunner(
    cfg.quiz_region,
    cfg.chat_box,
    cfg.response_region,
    options,
    cfg.option_base,
    gui=ui,
)
runner.start()             # capture + worker threads
```
The window updates with question count, average response time, tokens, and errors as the runner progresses.

## Troubleshooting
* **PyAutoGUI fails to control the screen** – ensure a desktop session is available. On Linux, run inside an X server (e.g. with `xvfb-run`) and grant screen‑recording permissions on macOS.
* **`pytesseract` cannot find Tesseract** – install the `tesseract-ocr` package and confirm the binary is on your `PATH` or set the `TESSERACT_CMD` environment variable.
* **No responses from OpenAI** – verify `OPENAI_API_KEY` and `OPENAI_MODEL` are set and that the machine has network access.
* **Environment variables ignored** – pass `--config` with the path to your `.env` file or export the variables before running the CLI.

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for a list of notable changes. Update this file with details for each new release.

## Tests
Run the test suite with coverage:
```bash
pytest --cov=quiz_automation
```
The CI workflow emits `coverage.xml`, which can be uploaded to a service like [Codecov](https://about.codecov.io/) or [Coveralls](https://coveralls.io/) for a coverage badge. After enabling a service, add its badge to the top of the README, for example with Codecov:

```markdown
[![codecov](https://codecov.io/gh/OWNER/basic-ai-auto-assistant/branch/main/graph/badge.svg)](https://codecov.io/gh/OWNER/basic-ai-auto-assistant)
```

Replace `OWNER` with your GitHub username.

Some tests rely on optional packages such as `numpy` and will be skipped when
those dependencies are missing. Install the extras for full coverage:

```bash
pip install -e .[full]
```
