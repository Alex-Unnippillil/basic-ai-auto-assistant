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
# QUIZ_REGION=[100,100,600,400]
# CHAT_BOX=[800,900]
# RESPONSE_REGION=[100,550,600,150]
# OPTION_BASE=[100,520]
```


## `quiz-automation` command
The package installs a `quiz-automation` script that wraps the command‑line interface in `run.py`.

### Optional dependencies
Running the command in a headless environment only needs `pydantic`, `pydantic-settings`, and `mss`.  Installing the following extras enables full desktop automation:

* `pyautogui` – screen control and screenshots
* `pytesseract` – OCR for ChatGPT's responses
* `opencv-python` – computer‑vision helpers
* `PySide6` – GUI for live statistics
* `numpy` – array helpers for CV routines

### Running
Invoke the script with a mode flag. Optional arguments control the backend,
question limit, logging, and configuration loading:

```bash


# Custom config and debug logging
quiz-automation --mode headless --log-level DEBUG --config settings.env
```


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

## Tests
Run the test suite with:
```bash
pytest
```
Some tests rely on optional packages such as `numpy` and will be skipped when
those dependencies are missing. Install the extras for full coverage:

```bash
pip install -e .[full]
```
