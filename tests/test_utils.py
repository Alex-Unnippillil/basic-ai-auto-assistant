from quiz_automation.utils import hash_text


def test_hash_text_consistent():
    assert hash_text("hello") == hash_text("hello")


def test_hash_text_different():
    assert hash_text("hello") != hash_text("world")
