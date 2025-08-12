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

## Running the entry script

`run.py` provides a small command-line interface.  The required screen regions and
answer options are read from environment variables or passed as arguments:

```bash
export QUIZ_REGION=100,100,600,400
export CHATGPT_BOX=800,900
export RESPONSE_REGION=100,550,600,150
export OPTION_BASE=100,520
export OPTIONS=ABCD
python run.py --mode headless
```

Each setting can also be specified directly on the command line:

```bash
python run.py --mode headless \
    --quiz-region 100,100,600,400 \
    --chatgpt-box 800,900 \
    --response-region 100,550,600,150 \
    --option-base 100,520 \
    --options ABCD
```

## Tests
Run the test suite with:
```bash
pytest
```
