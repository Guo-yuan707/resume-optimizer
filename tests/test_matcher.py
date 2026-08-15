"""matcher 模块的测试(第 3 课的函数)。

测什么:
    match_keywords() 的关键行为:
    - 命中/缺失的分类对不对
    - 大小写不敏感(Python == python)
    - 匹配率算得对不对
    - 空关键词列表不崩

怎么跑(在项目根目录):
    .venv/Scripts/python -m pytest tests/test_matcher.py -v
"""
from resume_optimizer.matcher import match_keywords

# 一段小简历文本,里面故意含有的词:Python、Git、SQL
SAMPLE_TEXT = "我熟悉 Python 和 Git,用 SQL 写过数据库查询。"


def test_hit_word():
    """简历里有的词,应该进 hit 列表。"""
    result = match_keywords(SAMPLE_TEXT, ["Python"])
    assert result["hit"] == ["Python"]
    assert result["miss"] == []
    assert result["results"]["Python"] is True


def test_miss_word():
    """简历里没有的词,应该进 miss 列表。"""
    result = match_keywords(SAMPLE_TEXT, ["Java"])
    assert result["hit"] == []
    assert result["miss"] == ["Java"]
    assert result["results"]["Java"] is False


def test_case_insensitive():
    """大小写不敏感:简历写 Python,关键词写 python,也该命中。"""
    result = match_keywords(SAMPLE_TEXT, ["python"])
    assert result["hit"] == ["python"]
    assert result["results"]["python"] is True


def test_mixed_hit_and_miss():
    """同时测命中+缺失,以及匹配率(3/4 = 0.75)。"""
    result = match_keywords(SAMPLE_TEXT, ["Python", "Git", "SQL", "Java"])
    assert result["hit"] == ["Python", "Git", "SQL"]
    assert result["miss"] == ["Java"]
    assert result["rate"] == 0.75


def test_empty_keywords():
    """空关键词列表:不崩,rate 是 0.0。"""
    result = match_keywords(SAMPLE_TEXT, [])
    assert result["hit"] == []
    assert result["miss"] == []
    assert result["rate"] == 0.0
