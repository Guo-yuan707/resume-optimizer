"""简历质量检查模块：对解析好的 Resume 对象逐项检查质量问题。

第 4 课：一组独立的检查规则 + check_all() 统一调度。
每条规则返回统一格式：{"rule": "规则名", "pass": True/False, "message": "说明"}
"""

from resume_optimizer.parser import Resume

def check_contact_info(header: list[str]) -> dict:
    """检查基本信息里有没有联系方式（邮箱或电话）。

    规则：header 里至少有一行包含 @（邮箱）或数字（电话）。
    如果没有，HR 没法联系你，这属于严重问题。

    参数:
        header: Resume.header，基本信息行列表

    返回:
        检查结果字典
    """
    try:
        # 把 header 里所有行拼成一段文字，方便搜索
        full_header = " ".join(header)

        has_email = "@" in full_header
        has_phone = any(char.isdigit() for char in full_header)

        if has_email and has_phone:
            return {
                "rule": "联系方式检查",
                "pass": True,
                "message": "✅ 找到了邮箱和电话，联系方式完整。",
            }
        elif has_email:
            return {
                "rule": "联系方式检查",
                "pass": False,
                "message": "⚠️ 找到了邮箱，但没找到电话号码。建议补充手机号。",
            }
        elif has_phone:
            return {
                "rule": "联系方式检查",
                "pass": False,
                "message": "⚠️ 找到了电话号码，但没找到邮箱。建议补充邮箱。",
            }
        else:
            return {
                "rule": "联系方式检查",
                "pass": False,
                "message": "❌ 没有找到邮箱和电话号码！HR 无法联系你，请务必添加。",
            }

    except Exception as e:
        # try/except 兜底：就算 header 是空的或者出了意外情况，
        # 检查函数本身不会崩溃，而是返回"检查失败"的结果
        return {
            "rule": "联系方式检查",
            "pass": False,
            "message": f"❌ 检查过程出错：{e}（header 可能为空或格式异常）",
        }


def check_section_length(section: list[str], section_name: str, min_lines: int = 2) -> dict:
    """检查某个段落的行数是否够多。

    规则：该段落至少有 min_lines 行（默认 2 行），否则显得内容空洞。

    参数:
        section:     段落的行列表（比如 Resume.skills）
        section_name: 段落名称，用于生成消息（比如 "专业技能"）
        min_lines:   最少需要几行，默认 2

    返回:
        检查结果字典
    """
    try:
        actual = len(section)

        if actual >= min_lines:
            return {
                "rule": f"{section_name}长度检查",
                "pass": True,
                "message": f"✅ {section_name}共 {actual} 行，内容充足。",
            }
        elif actual > 0:
            return {
                "rule": f"{section_name}长度检查",
                "pass": False,
                "message": f"⚠️ {section_name}只有 {actual} 行（建议至少 {min_lines} 行），内容偏少，可以再丰富一下。",
            }
        else:
            return {
                "rule": f"{section_name}长度检查",
                "pass": False,
                "message": f"❌ {section_name}没有内容！这一栏不能为空，请补充。",
            }

    except Exception as e:
        return {
            "rule": f"{section_name}长度检查",
            "pass": False,
            "message": f"❌ 检查过程出错：{e}",
        }


def check_empty_items(section: list[str], section_name: str) -> dict:
    """检查段落里有没有"看起来是空"的行。

    规则：每行的内容去掉首尾空白后，如果长度小于 2 个字符，
    很可能是一个空的项目符号（比如只写了 "-"）。

    参数:
        section:     段落的行列表
        section_name: 段落名称

    返回:
        检查结果字典
    """
    try:
        # 找出所有"太短"的行（去掉空白后不到 2 个字符）
        suspicious = []
        for i, line in enumerate(section):
            cleaned = line.strip()
            if len(cleaned) < 2:
                suspicious.append(f"第{i + 1}行")

        if len(suspicious) == 0:
            return {
                "rule": f"{section_name}空项检查",
                "pass": True,
                "message": f"✅ {section_name}没有空项，每行都有内容。",
            }
        else:
            return {
                "rule": f"{section_name}空项检查",
                "pass": False,
                "message": f"⚠️ {section_name}里发现 {len(suspicious)} 行疑似空的：{', '.join(suspicious)}。请检查是否写了内容。",
            }

    except Exception as e:
        return {
            "rule": f"{section_name}空项检查",
            "pass": False,
            "message": f"❌ 检查过程出错：{e}",
        }


def check_total_length(resume: Resume, min_chars: int = 300) -> dict:
    """检查简历整体是否太短。

    规则：把所有字段的文字拼起来，总字符数至少 min_chars（默认 300）。
    太短的简历 HR 会觉得没内容可看。

    参数:
        resume:    Resume 对象
        min_chars: 最少总字符数，默认 300

    返回:
        检查结果字典
    """
    try:
        # 把所有段落的行拼成一个大字符串
        all_text = ""
        for field_name in ["header", "skills", "education", "projects", "strengths"]:
            lines = getattr(resume, field_name, [])
            all_text += " ".join(lines)

        total = len(all_text)

        if total >= min_chars:
            return {
                "rule": "简历整体长度检查",
                "pass": True,
                "message": f"✅ 简历总长度 {total} 字，内容充实。",
            }
        else:
            return {
                "rule": "简历整体长度检查",
                "pass": False,
                "message": f"⚠️ 简历总长度只有 {total} 字（建议至少 {min_chars} 字），内容偏少，建议补充项目细节。",
            }

    except Exception as e:
        return {
            "rule": "简历整体长度检查",
            "pass": False,
            "message": f"❌ 检查过程出错：{e}",
        }
def check_education_quality(education: list[str]) -> dict:
    """检查教育经历里有没有提到学历或学校相关的关键词。

    规则：把教育经历所有行拼成一段文字，看里面有没有
    "大学"、"学院"、"本科"、"硕士"、"专科" 中任意一个。
    如果都没有，说明教育经历写得不够具体，HR 可能看不出你的学历。

    参数:
        education: 教育经历的行列表

    返回:
        检查结果字典
    """
    try:
        # 把所有行拼成一段，方便搜索
        full_text = "".join(education)

        # 学历/学校相关关键词
        edu_keywords = ["大学", "学院", "本科", "硕士", "专科"]

        # 检查每个关键词，看有没有出现在文本里
        found = []
        for kw in edu_keywords:
            if kw in full_text:
                found.append(kw)

        if found:
            return {
                "rule": "教育经历质量检查",
                "pass": True,
                "message": f"✅ 教育经历里提到了：{'、'.join(found)}。",
            }
        else:
            return {
                "rule": "教育经历质量检查",
                "pass": False,
                "message": "⚠️ 教育经历里没有提到大学/学院或学历（本科/硕士/专科），建议补充具体学校和学历信息。",
            }

    except Exception as e:
        return {
            "rule": "教育经历质量检查",
            "pass": False,
            "message": f"❌ 检查过程出错：{e}",
        }


def check_all(resume: Resume) -> list[dict]:
    """跑所有质量检查规则，返回结果列表。

    这是模块的入口函数：调用方只需要传一个 Resume 对象，
    就能拿到所有检查结果。加新规则时在这里加一行即可。

    参数:
        resume: Resume 对象（已经解析好的结构化简历）

    返回:
        一个列表，每个元素是一条检查结果的字典。
        格式：[{rule, pass, message}, ...]
    """
    results = []

    # --- 基本信息 ---
    results.append(check_contact_info(resume.header))

    # --- 各段落长度 ---
    results.append(check_section_length(resume.skills, "专业技能"))
    results.append(check_section_length(resume.education, "教育经历"))
    results.append(check_section_length(resume.projects, "项目经历"))
    results.append(check_section_length(resume.strengths, "个人优势"))

    # --- 空项检查（只查技能和项目，这两栏最容易出现空行）---
    results.append(check_empty_items(resume.skills, "专业技能"))
    results.append(check_empty_items(resume.projects, "项目经历"))

    # --- 整体长度 ---
    results.append(check_total_length(resume))

    # --- 教育经历质量 ---
    results.append(check_education_quality(resume.education))
    return results
