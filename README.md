# Quiz Automation

## Overview
The `quiz_automation` package demonstrates how to automate multiple‑choice quizzes by controlling the ChatGPT web interface.  Screenshots of the question are pasted into ChatGPT, the model's response is OCR'd, and the chosen option is clicked on screen.  Heavy desktop automation dependencies are optional and replaced with light stand‑ins when unavailable.

Core modules provide:
- high level helpers to paste images, read responses, and click answers
- a threaded runner that repeatedly captures questions, asks ChatGPT, and records metrics
- a PySide6 GUI that displays live statistics
- utilities for monitoring new questions, selecting screen regions, and simple CV heuristics

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
The requirements file installs everything needed to run the full automation.  For a minimal, headless setup only `pydantic`, `pydantic-settings`, and `mss` are necessary.  Optional extras that enable real desktop interaction are:

* `pyautogui` – screen control and screenshots
* `pytesseract` – OCR for ChatGPT's responses
* `opencv-python` – computer‑vision helpers
* `PySide6` – GUI for live statistics

## `quiz-automation` command
The package installs a `quiz-automation` script that wraps the command‑line interface in `run.py`.

### Environment variables
Set `OPENAI_API_KEY` for access to the OpenAI API.  Additional settings read by the tool include `OPENAI_MODEL`, `OPENAI_SYSTEM_PROMPT`, `POLL_INTERVAL`, `MODEL_NAME`, and `TEMPERATURE`.

An example `.env` file:

```dotenv
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=o4-mini-high
# OPENAI_SYSTEM_PROMPT="Reply with JSON {'answer':'A|B|C|D'}"
# POLL_INTERVAL=1.0
# MODEL_NAME=o4-mini-high
# TEMPERATURE=0.0
```

### Optional dependencies
Running the command in a headless environment only needs `pydantic`, `pydantic-settings`, and `mss`.  Installing the following extras enables full desktop automation:

* `pyautogui` – screen control and screenshots
* `pytesseract` – OCR for ChatGPT's responses
* `opencv-python` – computer‑vision helpers
* `PySide6` – GUI for live statistics

### Running
Invoke the script with a mode flag:

```bash
# headless
quiz-automation --mode headless

# GUI
quiz-automation --mode gui
```

## CLI example
```python
from quiz_automation.automation import answer_question_via_chatgpt
from quiz_automation.stats import Stats
import pyautogui

quiz_region = (100, 100, 600, 400)
chatgpt_box = (800, 900)
response_region = (100, 550, 600, 150)
option_base = (100, 520)
options = list("ABCD")

img = pyautogui.screenshot(quiz_region)
letter = answer_question_via_chatgpt(img, chatgpt_box, response_region, options, option_base, stats=Stats())
print(f"Model chose {letter}")
```
This snippet grabs the current question, asks ChatGPT for help, and clicks the selected answer.  Adjust the coordinates to match your screen layout.

## GUI example
```python
from quiz_automation.gui import QuizGUI
from quiz_automation.runner import QuizRunner

quiz_region = (100, 100, 600, 400)
chatgpt_box = (800, 900)
response_region = (100, 550, 600, 150)
option_base = (100, 520)
options = list("ABCD")

ui = QuizGUI()
runner = QuizRunner(quiz_region, chatgpt_box, response_region, options, option_base, gui=ui)
runner.start()             # capture + worker threads
```
The window updates with question count, average response time, tokens, and errors as the runner progresses.

## Tests
Run the test suite with:
```bash
pytest
```
