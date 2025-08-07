from quiz_automation import automation


def test_answer_question(monkeypatch):
    # Mock pyautogui functions
    actions = []

    monkeypatch.setattr(automation.pyautogui, "hotkey", fake_hotkey)
    monkeypatch.setattr(automation.pyautogui, "click", fake_click)
    monkeypatch.setattr(automation.pyautogui, "press", fake_press)
    monkeypatch.setattr(automation.pyautogui, "screenshot", fake_screenshot)
    monkeypatch.setattr(automation.pyautogui, "moveTo", lambda x, y: None)
