# Basic AI Auto Assistant

## Purpose
The project automates answering multiple‑choice quizzes by interacting with the ChatGPT web interface. It captures quiz images, forwards them to ChatGPT, and selects answers on the user's behalf, tracking performance statistics along the way.

## Architecture and Major Components
- **`quiz_automation/automation.py`** – low‑level helpers for pasting screenshots into ChatGPT, reading OCR responses, and clicking answer options while gracefully degrading when desktop automation libraries are missing
- **`quiz_automation/chatgpt_client.py`** – wrapper around the OpenAI SDK that requests a single‑letter answer with retry logic
- **`quiz_automation/model_client.py`** – lightweight heuristic model used when no OpenAI key is available.
- **`quiz_automation/gui.py`** – minimal PySide6 GUI that displays live quiz metrics such as questions answered, average response time and token usage
- **`quiz_automation/stats.py`** – dataclass for recording per‑question timings, token counts and errors
- **`quiz_automation/runner.py`** – thread that orchestrates screenshot capture and model interaction while updating the GUI with results
- **`quiz_automation/watcher.py`** – background monitor that polls the screen for new quiz questions and emits events when content changes
- Additional helpers such as `region_selector.py` for defining screen regions and `utils.py` for hashing text or copying images to the clipboard.

## Installation
1. Ensure **Python 3.11+** is installed.
2. Clone the repository and change into the project directory.
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

The main dependencies include PySide6 for the GUI, pyautogui and pytesseract for UI automation and OCR, mss for screen capture, and optional OpenAI SDK support defined in `requirements.txt`.

## Running the GUI
Execute the entry point to launch the quiz statistics window:
```bash
python run.py
```
This starts a tiny window showing live metrics via the `QuizGUI` class. Some features require desktop automation libraries; when unavailable the application falls back to no‑op behaviour suitable for headless testing.

## Running Tests
The project uses `pytest` for its test suite. From the repository root run:
```bash
pytest
```

## Contributing and Coding Standards
Contributions are welcome! Please follow these guidelines:
- Use type hints and keep functions small and well documented.
- Run `ruff` and `pytest` before submitting pull requests to ensure code style and tests pass.
- Adhere to PEP 8 conventions and maintain existing module structures.
- Describe your changes clearly in commit messages and pull requests.
