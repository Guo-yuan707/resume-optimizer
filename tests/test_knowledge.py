"""测试 knowledge.py 的纯逻辑部分:chunk_text / _split_long_line。

测试边界:只测"字符串进 → 列表出"的纯函数，不测读磁盘文件的 read_knowledge_files。
"""

from resume_optimizer import knowledge
from resume_optimizer.knowledge import chunk_text


def test_chunk_empty_string():
    """空字符串 → 空列表。"""
    assert chunk_text("") == []


def test_chunk_one_short_line():
    """单独一个短行 → 变成单独一个块。"""
    text = "岗位名称:AI 应用开发工程师"
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == "岗位名称:AI 应用开发工程师"


def test_chunk_multiple_short_lines():
    """多行短句 → 每行各成一个块。"""
    text = "岗位名称:AI 应用开发工程师\n公司类型:中小型 AI 创业公司\n工作地点:杭州"
    chunks = chunk_text(text)
    assert len(chunks) == 3
    assert "岗位名称" in chunks[0]
    assert "公司类型" in chunks[1]
    assert "工作地点" in chunks[2]


def test_chunk_skips_empty_lines():
    """空行(含只有空格的行) → 被跳过，不出现在结果里。"""
    text = "第一行\n\n\n第二行\n   \n第三行"
    chunks = chunk_text(text)
    assert len(chunks) == 3
    assert chunks == ["第一行", "第二行", "第三行"]


def test_chunk_paragraph_boundary_via_blank_line():
    """按空行拆段落:空行是段落边界，但块本身按行拆。"""
    text = "职责:\n开发 API\n维护数据库\n\n要求:\nPython 熟练\nSQL 熟练"
    chunks = chunk_text(text)
    # "职责:" + "开发 API" + "维护数据库" = 3, "要求:" + "Python 熟练" + "SQL 熟练" = 3 → 共 6
    assert len(chunks) == 6
    assert chunks[0] == "职责:"
    assert chunks[1] == "开发 API"
    assert chunks[2] == "维护数据库"
    assert chunks[3] == "要求:"
    assert chunks[4] == "Python 熟练"
    assert chunks[5] == "SQL 熟练"


def test_chunk_long_line_split_by_punctuation():
    """一行超过 100 字时，会在标点处切开(不把句子腰斩)。"""
    # 造一行 120 字的句子(用中文逗号隔开)
    part = "这是一个很长的句子用来测试切块功能，"
    long_line = part * 10  # 10 个 part，每个约 18 字 → 总共约 180 字，远超过默认 chunk_size=100
    chunks = chunk_text(long_line)
    # 应该被切成多块
    assert len(chunks) >= 2
    # 每块不应该超过 chunk_size 太多(允许一点余量因为标点位置)
    for c in chunks:
        assert len(c) <= 120  # 不会太离谱


def test_chunk_preserves_order():
    """切出来的块保持原文顺序。"""
    text = "第一行\n第二行\n第三行\n第四行\n第五行"
    chunks = chunk_text(text)
    joined = "".join(chunks)
    # 去掉所有空白后比:原文去掉换行 vs chunks 拼在一起
    assert joined == "第一行第二行第三行第四行第五行"


# ===== 第 13 课:build_knowledge_context(查书助手) =====
# 它默认读"真知识库"(examples/knowledge/),直接测会依赖真实文件、不稳定。
# 用 tmp_path 临时造一个"专属知识库" + monkeypatch 把路径指过去,完全可控、不碰真库。

def test_build_knowledge_context_finds_related(tmp_path, monkeypatch):
    """临时知识库里有一份 Python 后端文档 → 用相关 JD 检索,返回的就是它。"""
    # 1. 在专属文件夹里造两份文档:一份相关(Python 后端),一份无关(前端)
    (tmp_path / "01-python-backend.txt").write_text(
        "岗位名称:Python 后端开发工程师\n要求:熟悉 Python、FastAPI、MySQL\n",
        encoding="utf-8",
    )
    (tmp_path / "02-frontend.txt").write_text(
        "岗位名称:前端开发工程师\n要求:熟悉 HTML、CSS、JavaScript\n",
        encoding="utf-8",
    )
    # 2. 用 monkeypatch 把知识库路径临时指到专属文件夹(测完自动还原)
    monkeypatch.setattr(knowledge, "KNOWLEDGE_DIR", str(tmp_path))

    # 3. 拿一份"找 Python 后端"的 JD 去检索,只要最相关的 1 块
    ctx = knowledge.build_knowledge_context(
        "招 Python 后端,要求熟悉 Python 和 FastAPI", top_k=1
    )
    assert ctx  # 非空
    # 搜到的是 Python 后端那份的内容(含 Python / FastAPI,因为 JD 里提了这两个词)
    assert "FastAPI" in ctx
    assert "Python" in ctx
    # 无关的前端那份不该出现在最相关的 1 块里
    assert "前端开发工程师" not in ctx


def test_build_knowledge_context_empty_knowledge_base(tmp_path, monkeypatch):
    """知识库为空(目录里没有任何 .txt)→ 返回空串,上层当"没带参考"处理。"""
    monkeypatch.setattr(knowledge, "KNOWLEDGE_DIR", str(tmp_path))  # tmp_path 是空文件夹
    assert knowledge.build_knowledge_context("随便一段 JD 文本") == ""
