from quiz_automation import automation


def test_answer_question(monkeypatch):
    # Mock pyautogui functions
    actions = []
    def fake_hotkey(*args):
        actions.append(("hotkey", args))
    def fake_click(x=None, y=None):
        actions.append(("click", x, y))
    def fake_press(key):
        actions.append(("press", key))
    def fake_screenshot(region=None):
        # Return a unique object each call
        return object()
    monkeypatch.setattr(automation.pyautogui, "hotkey", fake_hotkey)
    monkeypatch.setattr(automation.pyautogui, "click", fake_click)
    monkeypatch.setattr(automation.pyautogui, "press", fake_press)
    monkeypatch.setattr(automation.pyautogui, "screenshot", fake_screenshot)
    monkeypatch.setattr(automation.pyautogui, "moveTo", lambda x, y: None)

    # Mock clipboard
    copied = {}
    def fake_copy(text):
        copied["text"] = text
    monkeypatch.setattr(automation.pyperclip, "copy", fake_copy)

    # Mock OCR
    calls = []
    def fake_ocr(img):
        calls.append(img)
        return "B" if len(calls) > 1 else "question"
    monkeypatch.setattr(automation.pytesseract, "image_to_string", fake_ocr)

    # Track click_option
    clicked = {}
    def fake_click_option(base, idx, offset=40):
        clicked["idx"] = idx
    monkeypatch.setattr(automation, "click_option", fake_click_option)

    resp = automation.answer_question((0,0,10,10), (1,1), (2,2,10,10), (3,3))
    assert resp == "B"
    assert clicked["idx"] == 1
    assert copied["text"] == "question"
    assert ("hotkey", ("alt", "tab")) in actions
