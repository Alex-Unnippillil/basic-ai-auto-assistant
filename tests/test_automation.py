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
        return object()

    monkeypatch.setattr(automation.pyautogui, "hotkey", fake_hotkey)
    monkeypatch.setattr(automation.pyautogui, "click", fake_click)
    monkeypatch.setattr(automation.pyautogui, "press", fake_press)
    monkeypatch.setattr(automation.pyautogui, "screenshot", fake_screenshot)
    monkeypatch.setattr(automation.pyautogui, "moveTo", lambda x, y: None)

    # Mock clipboard helper
    copied = {}

    def fake_copy_image(img):
        copied["img"] = img

    monkeypatch.setattr(automation, "copy_image_to_clipboard", fake_copy_image)

    # Mock response reader
    monkeypatch.setattr(
        automation, "read_chatgpt_response", lambda region, timeout=20, retries=1: "B"
    )

    # Track click_option
    clicked = {}

    def fake_click_option(base, idx, offset=40):
        clicked["idx"] = idx

    monkeypatch.setattr(automation, "click_option", fake_click_option)

    resp = automation.answer_question((0, 0, 10, 10), (1, 1), (2, 2, 10, 10), (3, 3))
    assert resp == "B"
    assert clicked["idx"] == 1
    assert "img" in copied
    assert ("hotkey", ("alt", "tab")) in actions


def test_read_chatgpt_response_refresh(monkeypatch):
    events = []

    def fake_hotkey(*args):
        events.append(args)

    def fake_screenshot(region=None):
        return object()

    outputs = ["", "answer"]

    def fake_ocr(img):
        return outputs.pop(0)

    # Simulate time so the first wait exceeds the timeout and triggers refresh
    times = iter([0, 0, 1.1, 1.1, 1.2])

    def fake_time():
        return next(times)

    monkeypatch.setattr(automation.pyautogui, "hotkey", fake_hotkey)
    monkeypatch.setattr(automation.pyautogui, "screenshot", fake_screenshot)
    monkeypatch.setattr(automation.pytesseract, "image_to_string", fake_ocr)
    monkeypatch.setattr(automation.time, "time", fake_time)
    monkeypatch.setattr(automation.time, "sleep", lambda x: None)

    text = automation.read_chatgpt_response((0, 0, 1, 1), timeout=1)
    assert text == "answer"
    assert ("ctrl", "r") in events
