from quiz_automation import automation
from quiz_automation.stats import Stats


class DummyModel:
    def __init__(self, answer: str = "A"):
        self.answer = answer
    def ask(self, question, options):
        self.seen = (question, tuple(options))
        return self.answer


def test_answer_question(monkeypatch):
    monkeypatch.setattr(automation.pyautogui, "screenshot", lambda region=None: "img")
    monkeypatch.setattr(automation.pyautogui, "moveTo", lambda x, y: None)
    monkeypatch.setattr(automation.pytesseract, "image_to_string", lambda img: "text")
    clicked = {}
    def fake_click(base, idx, offset=40):
        clicked["idx"] = idx
    monkeypatch.setattr(automation, "click_option", fake_click)

    model = DummyModel("C")
    stats = Stats()
    letter = automation.answer_question((0,0,10,10), ["o1","o2","o3"], (5,5), model, stats=stats)
    assert letter == "C"
    assert clicked["idx"] == 2
    assert model.seen == ("text", ("o1","o2","o3"))
    assert stats.summary()["questions"] == 1
