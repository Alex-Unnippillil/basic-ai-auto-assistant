import pytest
import quiz_automation.region_selector as rs_mod


@pytest.mark.skipif(
    not hasattr(rs_mod, "RegionSelector"),
    reason="RegionSelector not implemented",
)
def test_region_selector_persistence(tmp_path, monkeypatch):
    path = tmp_path / "coords.json"
    selector = rs_mod.RegionSelector(path)
    positions = iter([(1, 2), (5, 6)])
    monkeypatch.setattr("builtins.input", lambda prompt="": None)
    monkeypatch.setattr(rs_mod.pyautogui, "position", lambda: next(positions))
    region = selector.select("quiz")
    assert region == (1, 2, 4, 4)

    selector2 = rs_mod.RegionSelector(path)
    assert selector2.load("quiz") == (1, 2, 4, 4)
