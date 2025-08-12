import quiz_automation.region_selector as rs_mod


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


def test_region_selector_list_regions(tmp_path, monkeypatch):
    path = tmp_path / "coords.json"
    selector = rs_mod.RegionSelector(path)
    positions = iter([(1, 2), (5, 6)])
    monkeypatch.setattr("builtins.input", lambda prompt="": None)
    monkeypatch.setattr(rs_mod.pyautogui, "position", lambda: next(positions))
    selector.select("quiz")

    regions = selector.list_regions()
    assert regions == {"quiz": (1, 2, 4, 4)}

    regions["quiz"] = (0, 0, 0, 0)
    assert selector.load("quiz") == (1, 2, 4, 4)


def test_region_selector_handles_bad_json(tmp_path, caplog):
    path = tmp_path / "coords.json"
    path.write_text("{not: valid json}", encoding="utf8")

    with caplog.at_level("WARNING"):
        selector = rs_mod.RegionSelector(path)

    assert selector.list_regions() == {}
    assert any("Malformed region file" in r.message for r in caplog.records)
