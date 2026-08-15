"""parser 模块的测试(第 1-2 课的函数)。

测什么:
    - read_text():      能从磁盘文件读出文本
    - parse_resume():   把标准格式的简历文本正确拆成 5 个字段

怎么跑(在项目根目录):
    .venv/Scripts/python -m pytest tests/test_parser.py -v
"""
from resume_optimizer.parser import read_text, parse_resume

# 一段"标准格式"的小简历(标题行 + 各段内容),专门用来测解析
SAMPLE_RESUME = """郭园
邮箱:guoyuan@example.com
电话:13800000000

专业技能
Python
数据分析

教育经历
郑州财经学院 本科

项目经历
用 Python 写了一个简历优化工具

个人优势
学习能力强
"""


def test_parse_resume_header():
    """基本信息:第一个标题之前的非空行都该进 header。"""
    resume = parse_resume(SAMPLE_RESUME)
    assert resume.header == ["郭园", "邮箱:guoyuan@example.com", "电话:13800000000"]


def test_parse_resume_skills():
    """专业技能:标题下面、下一个标题之前的行都该进 skills。"""
    resume = parse_resume(SAMPLE_RESUME)
    assert resume.skills == ["Python", "数据分析"]


def test_parse_resume_education():
    resume = parse_resume(SAMPLE_RESUME)
    assert resume.education == ["郑州财经学院 本科"]


def test_parse_resume_projects():
    resume = parse_resume(SAMPLE_RESUME)
    assert resume.projects == ["用 Python 写了一个简历优化工具"]


def test_parse_resume_strengths():
    resume = parse_resume(SAMPLE_RESUME)
    assert resume.strengths == ["学习能力强"]


def test_parse_resume_empty_text():
    """空文本不该崩,5 个字段都应该是空列表。"""
    resume = parse_resume("")
    assert resume.header == []
    assert resume.skills == []
    assert resume.education == []
    assert resume.projects == []
    assert resume.strengths == []


def test_read_text_reads_real_file():
    """读项目里的示例简历:应该能读到内容,并且里面有"张三"。"""
    text = read_text("examples/resume.txt")
    assert len(text) > 0
    assert "张三" in text
