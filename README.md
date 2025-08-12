# Basic AI Auto Assistant

## Project Goals
The project automates solving multiple-choice quizzes by capturing questions, sending them to ChatGPT, and clicking the model's suggested answer. It provides a lightweight framework to explore screen automation and simple GUI updates.

## Architecture Overview
- **Watcher** – monitors a screen region for new questions and emits events when the content changes.
- **QuizRunner** – captures questions, asks ChatGPT for responses, and clicks the selected option.
- **GUI** – small PySide6 window showing real-time quiz metrics.
- **Utilities** – helpers for ChatGPT interaction, region selection, configuration, and statistics.

## Installation
1. Ensure Python 3.11+ is installed.
2. Clone the repository and create a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Major packages include:
   - `mss`, `pytesseract`, `opencv-python`, `numpy`
   - `pyautogui`, `PySide6`
   - `pydantic`, `pydantic-settings`, `python-dotenv`, `pyperclip`
   - Development tools: `pytest` and `ruff`

## Basic Usage
1. **Configure screen regions** with the `RegionSelector` helper:
   ```python
   from pathlib import Path
   from quiz_automation.region_selector import RegionSelector

   selector = RegionSelector(Path("regions.json"))
   quiz_region = selector.select("quiz")          # question area
   chatgpt_box = selector.select("chatgpt_box")   # chat input field
   response_region = selector.select("response")  # ChatGPT reply area
   ```
   Regions are saved to `regions.json` and can be reloaded with `selector.load(name)`.

2. **Set environment variables**:
   - `OPENAI_API_KEY` – API key used for ChatGPT requests.
   - `POLL_INTERVAL` – optional delay between screen polls (defaults to `1.0`).

3. **Run the assistant**:
   ```bash
   python run.py
   ```

## Contributing
1. Fork the repository and create a feature branch.
2. Follow existing code style and add tests for new features.
3. Run linters and tests before submitting:
   ```bash
   ruff .
   pytest
   ```
4. Commit your changes and open a pull request describing your work.

## Testing
Run the full test suite using:
```bash
pytest
```
