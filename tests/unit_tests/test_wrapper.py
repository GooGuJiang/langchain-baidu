from langchain_baidu._utilities import BaiduSearchAPIWrapper


def test_clean_text_removes_control_characters() -> None:
    wrapper = BaiduSearchAPIWrapper()
    dirty = "\n圆头\u200b耄耋\ue610 \n"
    assert wrapper.clean_text(dirty) == "圆头耄耋"


def test_normalize_url_handles_relative_paths() -> None:
    wrapper = BaiduSearchAPIWrapper()
    assert (
        wrapper._normalize_url("/link?id=1")
        == "https://www.baidu.com/link?id=1"
    )
