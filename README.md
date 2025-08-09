# Basic AI Auto Assistant

## Setup

The application reads configuration from environment variables. The most
important ones are:

| Variable | Description | Default |
|---------|-------------|---------|
| `OPENAI_API_KEY` | API key for OpenAI requests. | _unset_ |
| `POLL_INTERVAL` | Delay (in seconds) between polling iterations. | `1.0` |

Set them before running the scripts, for example:

```bash
export OPENAI_API_KEY="sk-..."
export POLL_INTERVAL=2.5  # optional
```

The `POLL_INTERVAL` variable is optional. If not provided, the system falls
back to a default of one second between polls.

