from unittest.mock import MagicMock, call

import pytest

from quiz_automation.clicker import Click, Clicker


def test_click_sequence_executes_clicks_and_delays():
    gui = MagicMock()
    sleeper = MagicMock()
    clicker = Clicker(gui=gui, sleep=sleeper)

    actions = [Click(1, 2, 0.5), Click(3, 4)]

    clicker.click_sequence(actions)

    assert gui.click.call_args_list == [call(x=1, y=2), call(x=3, y=4)]
    sleeper.assert_called_once_with(0.5)


def test_click_negative_delay_raises_value_error():
    clicker = Clicker(gui=MagicMock(), sleep=MagicMock())

    with pytest.raises(ValueError):
        clicker.click(1, 2, -1)
