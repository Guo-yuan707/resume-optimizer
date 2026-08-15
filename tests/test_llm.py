"""llm 模块的测试(第 8 课)。

测什么:
    只测 parse_keyword_json() —— 它是纯逻辑、不调 API、不花钱。
    不测 extract_keywords_from_jd() —— 它要调 DeepSeek 真实 API,
    测试不该依赖网络、不该花钱(第 7 课的"测试边界"意识)。

怎么跑(在项目根目录):
    .venv/Scripts/python -m pytest tests/test_llm.py -v
"""
import pytest

from resume_optimizer.llm import parse_keyword_json, build_rewrite_prompt


def test_clean_json():
    """最干净的情况:整段就是 JSON 数组。"""
    assert parse_keyword_json('["Python", "API"]') == ["Python", "API"]


def test_markdown_code_block():
    """AI 不老实,包了 markdown 代码块 → 照样抠出来。"""
    raw = '```json\n["Python", "API"]\n```'
    assert parse_keyword_json(raw) == ["Python", "API"]


def test_surrounded_by_text():
    """AI 前后夹带解释文字 → 只取方括号里的部分。"""
    raw = '提取到的关键词如下:["Python", "API"] 请查收。'
    assert parse_keyword_json(raw) == ["Python", "API"]


def test_chinese_keywords():
    """中英文关键词混着,都能解析。"""
    raw = '["Python", "数据分析", "API"]'
    assert parse_keyword_json(raw) == ["Python", "数据分析", "API"]


def test_empty_array():
    """空数组 → 空列表。"""
    assert parse_keyword_json("[]") == []


def test_filter_empty_strings():
    """数组里有空字符串 → 被过滤掉。"""
    assert parse_keyword_json('["Python", "", "API", " "]') == ["Python", "API"]


def test_garbage_raises():
    """纯垃圾文本,解析不了 → 抛 ValueError(让上层给用户友好提示)。"""
    with pytest.raises(ValueError):
        parse_keyword_json("这不是JSON,也不是数组")


# ===== 第 12/13 课:build_rewrite_prompt 的 knowledge_context 行为 =====
# 拼 prompt 是纯函数(字符串进 → 字符串出),不调 API、不花钱,值得锁住。
# 三个用例正好覆盖:传了 / 没传 / 传空串(空串 = 没传)。

def test_rewrite_prompt_includes_knowledge():
    """传了 knowledge_context → prompt 里出现【岗位知识参考】和具体内容。"""
    ctx = "1. 负责基于 LLM 的 AI 应用开发\n2. 了解 RAG 相关技术"
    prompt = build_rewrite_prompt(
        "简历内容",
        {"hit": [], "miss": ["Python"], "rate": 0.0},
        [],
        knowledge_context=ctx,
    )
    assert "【岗位知识参考】" in prompt
    assert "负责基于 LLM 的 AI 应用开发" in prompt


def test_rewrite_prompt_without_knowledge():
    """不传 → prompt 里没有【岗位知识参考】(跟第 9 课一样)。"""
    prompt = build_rewrite_prompt(
        "简历内容",
        {"hit": [], "miss": ["Python"], "rate": 0.0},
        [],
    )
    assert "【岗位知识参考】" not in prompt


def test_rewrite_prompt_empty_knowledge_same_as_none():
    """传空串 → 等同没传,不出现参考段。"""
    prompt = build_rewrite_prompt(
        "简历内容",
        {"hit": [], "miss": ["Python"], "rate": 0.0},
        [],
        knowledge_context="",
    )
    assert "【岗位知识参考】" not in prompt
