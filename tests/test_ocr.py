import quiz_automation.ocr as ocr_module

class DummyBackendOne:
    def __call__(self, img):  # pragma: no cover - simple stub
        return "one"

class DummyBackendTwo:
    def __call__(self, img):  # pragma: no cover - simple stub
        return "two"

def test_get_backend_registered(monkeypatch):
    monkeypatch.setattr(ocr_module, "_BACKENDS", dict(ocr_module._BACKENDS))
    ocr_module.register_backend("one", DummyBackendOne)
    backend = ocr_module.get_backend("one")
    assert backend("img") == "one"


def test_get_backend_dynamic_import():
    backend = ocr_module.get_backend("tests.test_ocr:DummyBackendTwo")
    assert backend("img") == "two"
