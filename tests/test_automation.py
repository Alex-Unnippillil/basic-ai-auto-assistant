from quiz_automation import automation
from quiz_automation.stats import Stats


class DummyPG:
    def screenshot(self, region=None):
        return "img"

    def moveTo(self, x, y):
        pass


class DummyPT:
    @staticmethod
    def image_to_string(img):
        return "text"


class DummyModel:
    def __init__(self, answer: str = "A"):
        self.answer = answer
        self.calls = 0
    def ask(self, question, options):
        self.calls += 1
        self.seen = (question, tuple(options))
        return self.answer


def test_answer_question(monkeypatch):
    monkeypatch.setattr(automation, "_pyautogui", lambda: DummyPG())
    monkeypatch.setattr(automation, "_pytesseract", lambda: DummyPT)
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


def test_answer_question_cache(monkeypatch):
    monkeypatch.setattr(automation, "_pyautogui", lambda: DummyPG())
    monkeypatch.setattr(automation, "_pytesseract", lambda: DummyPT)
    clicked = {}

    def fake_click(base, idx, offset=40):
        clicked.setdefault("count", 0)
        clicked["count"] += 1

    monkeypatch.setattr(automation, "click_option", fake_click)

    model = DummyModel("B")
    stats = Stats()
    automation.answer_question((0,0,10,10), ["o1","o2"], (5,5), model, stats=stats)
    automation.answer_question((0,0,10,10), ["o1","o2"], (5,5), model, stats=stats)
    assert model.calls == 1
    assert clicked["count"] == 2
