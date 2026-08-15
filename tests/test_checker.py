"""checker 模块的测试(第 4 课的函数)。

测什么:
    每条检查规则对"合格数据"应该放行(pass=True),
    对"不合格数据"应该拦截(pass=False)。
    最后验证 check_all() 返回 9 条、格式统一。

怎么跑(在项目根目录):
    .venv/Scripts/python -m pytest tests/test_checker.py -v
"""
from resume_optimizer.parser import Resume
from resume_optimizer.checker import (
    check_contact_info,
    check_section_length,
    check_empty_items,
    check_total_length,
    check_education_quality,
    check_all,
)


def make_resume(**kwargs):
    """造一个 Resume 对象,没给的字段默认空列表,省得每次写全。"""
    defaults = {
        "header": [],
        "skills": [],
        "education": [],
        "projects": [],
        "strengths": [],
    }
    defaults.update(kwargs)
    return Resume(**defaults)


# ---------- 联系方式检查 ----------

def test_contact_ok():
    """有邮箱和电话 → 通过。"""
    r = check_contact_info(["郭园", "邮箱:g@x.com", "电话:13800000000"])
    assert r["pass"] is True


def test_contact_no_email_no_phone():
    """只有名字,没邮箱没电话 → 不通过。"""
    r = check_contact_info(["郭园"])
    assert r["pass"] is False


# ---------- 段落长度检查 ----------

def test_section_length_ok():
    """2 行以上 → 通过。"""
    r = check_section_length(["Python", "Git"], "专业技能")
    assert r["pass"] is True


def test_section_length_empty():
    """空段落 → 不通过。"""
    r = check_section_length([], "项目经历")
    assert r["pass"] is False


# ---------- 空项检查 ----------

def test_empty_items_ok():
    """每行都有内容 → 通过。"""
    r = check_empty_items(["正常的一行内容", "也正常"], "专业技能")
    assert r["pass"] is True


def test_empty_items_found():
    """有一行只有 '-' → 不通过。"""
    r = check_empty_items(["正常的一行内容", "-"], "项目经历")
    assert r["pass"] is False


# ---------- 整体长度检查 ----------

def test_total_length_ok():
    """内容超过 min_chars 时 → 通过。
    (用 min_chars=10 而不是默认 300:测试里的简历是几行小样例,
    但函数逻辑一样——够长就放行。)"""
    resume = make_resume(
        header=["郭园", "邮箱:g@x.com"],
        skills=["Python", "Git", "SQL"],
        education=["郑州财经学院 本科"],
        projects=["用 Python 写了简历优化工具"],
        strengths=["学习能力强"],
    )
    r = check_total_length(resume, min_chars=10)
    assert r["pass"] is True


def test_total_length_empty():
    """全部空的简历 → 不通过。"""
    r = check_total_length(make_resume())
    assert r["pass"] is False


# ---------- 教育经历质量检查 ----------

def test_education_quality_ok():
    """提到了"学院"和"本科" → 通过。"""
    r = check_education_quality(["郑州财经学院 本科"])
    assert r["pass"] is True


def test_education_quality_missing():
    """完全没提学校/学历 → 不通过。"""
    r = check_education_quality(["在校期间担任班长"])
    assert r["pass"] is False


# ---------- check_all 总入口 ----------

def test_check_all_returns_nine_results():
    """check_all 应该返回 9 条,每条都有 rule/pass/message 三个键。"""
    resume = make_resume(
        header=["郭园", "邮箱:g@x.com", "电话:13800000000"],
        skills=["Python", "Git", "SQL"],
        education=["郑州财经学院 本科"],
        projects=["用 Python 写了简历优化工具", "负责前后端联调"],
        strengths=["学习能力强", "责任心强"],
    )
    results = check_all(resume)

    assert len(results) == 9
    for r in results:
        assert "rule" in r
        assert "pass" in r
        assert "message" in r
