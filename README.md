# Basic AI Auto Assistant

Basic AI Auto Assistant automates answering multiple-choice quiz questions by leveraging OpenAI's API and screen automation tools.

## Setup

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in the values
   - At minimum set your OpenAI API key

## Environment Variables

| Variable         | Description                                  |
| ---------------- | -------------------------------------------- |
| `OPENAI_API_KEY` | Required. OpenAI API key used for ChatGPT.   |
| `POLL_INTERVAL`  | Optional. Seconds between screen polls.      |

## Verification

Run the following commands to ensure the project is set up correctly:

```bash
python -m ruff check
pytest -q
```

## Troubleshooting

- **openai package not available**: Ensure `openai` is installed and `OPENAI_API_KEY` is set.
- **Tests failing due to missing system packages**: Verify all dependencies from `requirements.txt` are installed inside the virtual environment.
- **Permission errors on macOS/Linux**: Make sure the scripts are executable and that your user has access to necessary system resources.

For additional issues, re-run the setup steps or search project issues for known problems.
