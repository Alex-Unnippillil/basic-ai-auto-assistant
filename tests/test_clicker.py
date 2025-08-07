from quiz_automation.clicker import click_option


def test_click_option(monkeypatch):
    moves = []
    clicks = []
    monkeypatch.setattr(
        "quiz_automation.clicker.pyautogui.moveTo", lambda x, y: moves.append((x, y))
    )
    monkeypatch.setattr("quiz_automation.clicker.pyautogui.click", lambda: clicks.append(True))
    click_option((10, 10), 1, offset=5)
    assert moves == [(10, 15)]
    assert clicks == [True]
