"""简历解析模块:负责把简历文件读成文本,再把文本拆成结构化数据。

第 1 课:read_text() 读纯文本文件
第 2 课:Resume 数据类 + parse_resume() 按标题分段解析
"""
from dataclasses import dataclass


@dataclass
class Resume:
    """简历数据结构:像一张固定栏位的表格,5 个字段各自是一个字符串列表。

    字段说明:
        header     — 基本信息(姓名、邮箱、电话等,在第一个标题之前的所有非空行)
        skills     — 专业技能下面的每一行
        education  — 教育经历下面的每一行
        projects   — 项目经历下面的每一行
        strengths  — 个人优势下面的每一行
    """
    header: list[str]
    skills: list[str]
    education: list[str]
    projects: list[str]
    strengths: list[str]


# 这四个词是你的简历里用到的标题,parse_resume() 靠它们识别段落分界
SECTION_TITLES = ["专业技能", "教育经历", "项目经历", "个人优势"]

# 标题名 → Resume 里的字段名(字符串,后面用 getattr 取到)
_TITLE_TO_FIELD = {
    "专业技能": "skills",
    "教育经历": "education",
    "项目经历": "projects",
    "个人优势": "strengths",
}


def read_text(path: str) -> str:
    """读取一个纯文本文件,返回里面的字符串内容。

    参数:
        path: 文件路径,例如 "examples/resume.txt"

    返回:
        文件里的全部文字
    """
    # "r" 表示读模式;encoding="utf-8" 保证能正确读出中文
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def parse_resume(text: str) -> Resume:
    """把一段简历文本按标题拆成结构化数据。

    思路(跟 scratch.py 练习的一样):
        1. 按换行切开
        2. 跳过空行
        3. 遇到已知标题 → 切换当前段落
        4. 普通行 → 归入当前段落

    参数:
        text: 整段简历文本

    返回:
        一个 Resume 对象,5 个字段都填好了
    """
    lines = text.split("\n")

    # 用 dict 暂存结果:key=字段名,value=该字段的内容行列表
    sections = {
        "header": [],
        "skills": [],
        "education": [],
        "projects": [],
        "strengths": [],
    }
    current_field = "header"  # 第一个标题之前的内容都归 header

    for line in lines:
        clean = line.strip()
        if clean == "":
            continue
        if clean in SECTION_TITLES:
            current_field = _TITLE_TO_FIELD[clean]
        else:
            sections[current_field].append(clean)

    # 用 dict 的值创建 Resume 对象(**sections 是把字典"拆开"传参的写法)
    return Resume(**sections)
