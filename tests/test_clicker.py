from quiz_automation import clicker
from quiz_automation.clicker import click_option


def test_click_option(monkeypatch):
    moves = []
    clicks = []
    class Dummy:
        def moveTo(self, x, y):
            moves.append((x, y))

        def click(self):
            clicks.append(True)

    monkeypatch.setattr(clicker, "_pyautogui", lambda: Dummy())
    click_option((10, 10), 1, offset=5)
    assert moves == [(10, 15)]
    assert clicks == [True]
