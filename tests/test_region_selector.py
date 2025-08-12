import pytest
import quiz_automation.region_selector as rs_mod
from quiz_automation.types import Region


def test_region_selector_persistence(tmp_path, monkeypatch):
    path = tmp_path / "coords.json"
    selector = rs_mod.RegionSelector(path)
    positions = iter([(1, 2), (5, 6)])
    monkeypatch.setattr("builtins.input", lambda prompt="": None)
    monkeypatch.setattr(rs_mod.pyautogui, "position", lambda: next(positions))
    region = selector.select("quiz")
    assert region == Region(1, 2, 4, 4)

    selector2 = rs_mod.RegionSelector(path)
    assert selector2.load("quiz") == Region(1, 2, 4, 4)


def test_region_selector_missing_file(tmp_path):
    path = tmp_path / "coords.json"
    selector = rs_mod.RegionSelector(path)
    with pytest.raises(KeyError):
        selector.load("quiz")


@pytest.mark.parametrize("content", ["{not json", '{"quiz": [1, 2, 3]}' ])
def test_region_selector_corrupted_file(tmp_path, content):
    path = tmp_path / "coords.json"
    path.write_text(content, encoding="utf8")
    selector = rs_mod.RegionSelector(path)
    with pytest.raises(KeyError):
        selector.load("quiz")
