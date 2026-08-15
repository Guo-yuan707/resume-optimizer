"""LLM 调用模块：封装 DeepSeek API。

第 5 课：根据分析结果生成简历优化建议。
第 8 课：从 JD 文本里自动提取关键词（结构化输出）。

核心职责：
    1. 从 .env 读取 API Key 和 Base URL
    2. 把匹配结果 + 检查结果拼成一段结构化的 prompt，返回优化建议
    3. 让 AI 从 JD 提取关键词（返回 JSON），并解析成关键词列表
    4. (第 9 课) 让 AI 输出一整份改写后的简历，供导出保存
"""
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from config import DEFAULT_MODEL, TEMPERATURE, MAX_TOKENS, REWRITE_MODEL, REWRITE_MAX_TOKENS

# 模块加载时就读 .env，保证 API Key 在需要时已经就绪
load_dotenv()


def _build_client() -> OpenAI:
    """创建并返回配置好的 OpenAI 客户端（指向 DeepSeek）。

    封装成函数的好处：
        - 每次调用时创建，不用全局变量
        - 出问题时能给出明确的错误提示

    返回:
        配置好的 OpenAI 客户端实例
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    if not api_key or api_key == "你的key填在这里":
        raise ValueError(
            "❌ 未设置 DEEPSEEK_API_KEY！\n"
            "请在项目根目录的 .env 文件里填入你的 DeepSeek API Key。\n"
            "去 https://platform.deepseek.com/api_keys 创建。"
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def _summarize_analysis(match_result: dict, check_results: list[dict]) -> str:
    """把匹配结果 + 检查结果压缩成几行文字，喂给 AI（第 9 课抽出的公共函数）。

    为什么抽出来？build_prompt（第 5 课）和 build_rewrite_prompt（第 9 课）
    都要把"匹配结果 + 检查结果"整理成给 AI 看的摘要，
    写两遍容易改一处忘另一处，所以合并成一个函数。
    函数名前加下划线 _ 表示"内部函数，别的文件别 import 我"。
    """
    hit_kws = match_result["hit"]
    miss_kws = match_result["miss"]
    rate = match_result["rate"]

    lines = [
        f"匹配率：{rate:.0%}（{len(hit_kws)}/{len(hit_kws) + len(miss_kws)}）",
        f"✅ 已命中关键词：{'、'.join(hit_kws)}",
        f"❌ 缺失关键词：{'、'.join(miss_kws)}" if miss_kws else "✅ 所有关键词都已命中！",
    ]
    for r in check_results:
        icon = "✅" if r["pass"] else "❌"
        lines.append(f"{icon} {r['message']}")

    return "\n".join(lines)


def build_prompt(
    resume_text: str,
    match_result: dict,
    check_results: list[dict],
    knowledge_context: str = "",
) -> str:
    """把简历文本、匹配结果、检查结果拼成给 AI 的 prompt。

    AI 需要三样信息才能给出有针对性的建议：
        1. 简历原文 — 知道在改什么
        2. 关键词匹配结果 — 知道缺了哪些技能词
        3. 质量检查结果 — 知道哪些段有问题

    第 12 课新增参数 knowledge_context：
        RAG 检索到的岗位知识参考段落。有值拼进去当【岗位知识参考】，
        建议贴合真实岗位要求；默认空串 = 不带参考（旧行为）。

    参数:
        resume_text:       简历全文（纯文本）
        match_result:      match_keywords() 的返回结果
        check_results:     check_all() 的返回结果
        knowledge_context: 第 12 课新增，岗位知识参考段落（默认空串）

    返回:
        一段结构化的 prompt 文本，直接发给 AI
    """
    # 匹配结果和检查结果压成几行文字，喂给 AI（公共函数 _summarize_analysis，第 9 课抽出）
    analysis_summary = _summarize_analysis(match_result, check_results)

    # 第 12 课新增：如果带了知识库参考，拼一段【岗位知识参考】进去（空串则这整段都不出现）
    knowledge_section = ""
    if knowledge_context.strip():
        knowledge_section = f"""
【岗位知识参考】（从真实岗位要求知识库中检索到的、与这份 JD 最相关的内容）
{knowledge_context}"""

    # --- 拼成最终 prompt ---
    prompt = f"""你是一位资深的简历优化专家。请根据以下信息，给出具体的简历优化建议。

【当前简历内容】
{resume_text}
{knowledge_section}
【分析摘要】
{analysis_summary}

【任务要求】
1. 针对「缺失的关键词」，建议如何在简历中自然地融入这些技能（不要硬塞，要结合项目经历来写）
2. 针对「未通过的质量检查」，给出具体的修改方案
3. 针对项目经历部分，建议如何用 STAR 法则（情境-任务-行动-结果）改写，让描述更有说服力
4. 最后给出一段改写示例（选一段项目经历来改写）
5. 特别关注简历的可读性和逻辑性，确保内容清晰、重点突出

请用中文回答，语气专业但亲切，像一位朋友在帮你改简历。"""

    return prompt


def get_optimization_advice(
    resume_text: str,
    match_result: dict,
    check_results: list[dict],
    model: str = DEFAULT_MODEL,
    knowledge_context: str = "",
) -> str:
    """调用 DeepSeek API，获取简历优化建议。

    这是模块的主入口函数：
        1. 构建 prompt
        2. 发送给 DeepSeek
        3. 返回 AI 的回复文本

    参数:
        resume_text:       简历全文
        match_result:      关键词匹配结果
        check_results:     质量检查结果
        model:             使用的模型名，默认 deepseek-v4-flash（快/便宜）
                           需要更高质量时传 "deepseek-v4-pro"
        knowledge_context: 第 12 课新增，岗位知识参考段落（默认空串）

    返回:
        AI 生成的优化建议（纯文本）
    """
    client = _build_client()
    prompt = build_prompt(resume_text, match_result, check_results, knowledge_context)

    # 调用 Chat Completion API
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一位资深的简历优化专家，擅长帮助求职者改进简历。你给出的建议具体、可操作，从不泛泛而谈。"
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=TEMPERATURE,  # 0.7 = 有一定创意但不离谱（0=死板，1=脑洞大）
        max_tokens=MAX_TOKENS,  # 4096 够 AI 输出完整建议（之前 2000 不够,经常截断）
    )

    # 取出 AI 的回复文本
    advice = response.choices[0].message.content
    finish = response.choices[0].finish_reason

    # 检查是否被硬截断:finish_reason == "length" 说明 max_tokens 不够
    if finish == "length":
        advice += "\n\n> ⚠️ **注意:AI 回复因字数限制被截断,建议调大 max_tokens 或精简 prompt 任务要求。**"

    return advice


def build_rewrite_prompt(
    resume_text: str,
    match_result: dict,
    check_results: list[dict],
    knowledge_context: str = "",
) -> str:
    """拼出"直接输出改写后整份简历"的 prompt（第 9 课）。

    和 build_prompt 的分工：
        build_prompt           → 让 AI 输出"优化建议"（哪里怎么改）
        build_rewrite_prompt   → 让 AI 输出"改好的成品"（一整份简历）

    关键设计：要求 AI 必须保留原简历的四个分段标题，一字不差。
    为什么？因为 parse_resume()（parser.py 的 SECTION_TITLES）就靠这几个标题切段，
    标题保住了，导出的文件还能被本工具再读回来分析，形成"改→查→再改"的循环。

    第 12 课新增参数 knowledge_context：
        RAG 检索到的岗位知识参考段落（knowledge.py 的 build_knowledge_context 拼好的）。
        有值时拼进 prompt 当【岗位知识参考】，让 AI"开卷考试"——改写时贴合真实岗位要求；
        默认空串 = 没有参考材料，行为跟第 9 课完全一样，所以旧调用不用改。
    """
    analysis_summary = _summarize_analysis(match_result, check_results)

    # 第 12 课新增：如果带了知识库参考，拼一段【岗位知识参考】进去（空串则这整段都不出现）
    knowledge_section = ""
    if knowledge_context.strip():
        knowledge_section = f"""
【岗位知识参考】（从真实岗位要求知识库中检索到的、与这份 JD 最相关的内容）
{knowledge_context}"""

    prompt = f"""你是一位资深的简历改写专家。请把下面的简历改写成一版【完整的新简历】，直接输出改写后的全文，不要任何解释或开场白。

【当前简历内容】
{resume_text}
{knowledge_section}
【分析摘要】
{analysis_summary}

【改写要求】
1. 输出一版完整的简历全文，不是建议、不是示例，是可直接保存使用的整份简历
2. 必须保留原简历的四个分段标题，一字不差：「专业技能」「教育经历」「项目经历」「个人优势」；标题只写纯文字，禁止加 ** 星号、# 号等任何 markdown 标记；标题下是各段内容；基本信息（姓名/联系方式）放在最前面，不带标题
3. 把「缺失的关键词」自然地融入相关段落（结合项目经历写，不要生硬堆砌）
4. 项目经历用 STAR 法则（情境-任务-行动-结果）改写，让描述更有说服力
5. 保持中文学术风格，语气正式、简洁、有力量

请用中文回答。"""

    return prompt


def get_rewritten_resume(
    resume_text: str,
    match_result: dict,
    check_results: list[dict],
    model: str = REWRITE_MODEL,
    knowledge_context: str = "",
) -> str:
    """调用 DeepSeek，让它输出一版完整的改写后简历（第 9 课）。

    和 get_optimization_advice 的区别：
        那个返回"建议"，这个返回"成品"——一整份可以直接存成文件的简历文本。

    参数:
        resume_text:       简历全文
        match_result:      关键词匹配结果
        check_results:     质量检查结果
        model:             用的模型，默认 REWRITE_MODEL（pro）。
                           "重写整份简历"比"给建议"更考验质量，所以默认用 pro。
        knowledge_context: 第 12 课新增。RAG 检索到的岗位知识参考段落，
                           默认空串（不带参考 = 旧行为）。

    返回:
        改写后的整份简历文本
    """
    client = _build_client()
    prompt = build_rewrite_prompt(resume_text, match_result, check_results, knowledge_context)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一位资深的简历改写专家，输出严谨、直接、可落地，从不废话。"
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=TEMPERATURE,  # 0.7 = 有一定创意但不离谱
        max_tokens=REWRITE_MAX_TOKENS,  # 整份简历输出长，用单独的上限 8192
    )

    rewritten = response.choices[0].message.content
    finish = response.choices[0].finish_reason

    # 检查是否被硬截断:finish_reason == "length" 说明 max_tokens 不够
    if finish == "length":
        rewritten += "\n\n> ⚠️ **注意:改写结果因字数限制被截断,建议调大 max_tokens。**"

    return rewritten


def parse_keyword_json(raw: str) -> list[str]:
    """把模型返回的文字解析成关键词列表（纯逻辑，不调 API，可测试）。

    AI 不一定老实：
        - 可能带 markdown 代码块：```json [...] ```
        - 可能前后夹带解释文字：提取到的关键词如下：["Python", "API"] 请查收
    所以做容错：先直接 json.loads，失败就正则抠出方括号数组再试。

    参数:
        raw: 模型返回的原始文本

    返回:
        关键词列表。彻底解析不了时抛 ValueError（让上层给用户友好提示）。
    """
    # 1. 先直接试：整段就是 JSON 数组
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(k).strip() for k in parsed if str(k).strip()]
    except (json.JSONDecodeError, TypeError):
        pass

    # 2. 用正则抠出 [ ... ] 的部分（re.DOTALL = 让 . 也能匹配换行）
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [str(k).strip() for k in parsed if str(k).strip()]
        except (json.JSONDecodeError, TypeError):
            pass

    # 3. 彻底失败：抛错，让上层给用户看明白的提示
    raise ValueError(f"无法从 AI 回复中解析出关键词列表。回复原文:\n{raw}")


def extract_keywords_from_jd(
    jd_text: str,
    model: str = DEFAULT_MODEL,
    max_keywords: int = 20,
) -> list[str]:
    """让 DeepSeek 从 JD 文本里提取关键词，返回关键词列表。

    思路（第 8 课）：
        1. 写一段"只要 JSON 数组"的 prompt，把 JD 文本喂给模型
        2. 调 DeepSeek（用低温度，提取要稳定、可复现）
        3. 调 parse_keyword_json 把回复解析成列表

    参数:
        jd_text:      职位描述全文
        model:        用的模型（默认 flash，快/便宜）
        max_keywords: 最多提取多少个关键词

    返回:
        关键词列表，例如 ["Python", "API", "数据分析"]
    """
    client = _build_client()

    prompt = f"""你是一位招聘信息分析助手。请从下面的职位描述（JD）中，提取最重要的 {max_keywords} 个技能/技术关键词。
要求：
1. 中英文都要提取（例如：Python、API、数据分析）
2. 只返回一个 JSON 数组，形如 ["Python", "API", "数据分析"]
3. 不要输出任何解释文字，不要用 markdown 代码块，只要数组本身

【JD 内容】
{jd_text}"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # 提取关键词要稳定，用低温度（0.7 是改写建议用的）
        max_tokens=500,   # 关键词列表很短，500 足够
    )

    raw = response.choices[0].message.content
    return parse_keyword_json(raw)
