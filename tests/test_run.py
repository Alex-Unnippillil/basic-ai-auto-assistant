from unittest.mock import MagicMock, patch

import run
from quiz_automation.stats import Stats


def test_headless_invokes_quiz_runner():
    with patch("run.QuizRunner") as MockRunner, \
         patch("run.ChatGPTClient", create=True) as MockChatGPTClient, \
         patch("run.LocalModelClient", create=True) as MockLocalModelClient:
        mock_runner = MagicMock()
        mock_runner.is_alive.return_value = False
        MockRunner.return_value = mock_runner

        run.main(["--mode", "headless", "--backend", "local", "--max-questions", "1"])

        MockRunner.assert_called_once()
        MockChatGPTClient.assert_not_called()
        MockLocalModelClient.assert_called_once_with()
        _, kwargs = MockRunner.call_args
        assert isinstance(kwargs.get("stats"), Stats)
        assert kwargs.get("model_client") is MockLocalModelClient.return_value
