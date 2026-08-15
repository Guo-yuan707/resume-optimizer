"""关键词匹配模块：把 JD 的关键词和简历做比对，算匹配度。

第 3 课：match_keywords() 纯关键词列表匹配
"""


def match_keywords(resume_text: str, keywords: list[str]) -> dict:
    """逐一检查每个关键词是否出现在简历文本中（忽略大小写）。

    思路：
        1. 把简历全文统一变小写（"Python" 和 "python" 能对上）
        2. 遍历每个关键词，用 in 检查是否在简历里
        3. 分别记到「命中」和「缺失」两个列表里
        4. 用 命中数 ÷ 总数 算出匹配率

    参数:
        resume_text: 整份简历的纯文本
        keywords:   JD 里提取的关键词列表

    返回:
        一个字典，包含：
        - 'results': {关键词: True/False}   — 每个词的匹配结果
        - 'hit':     [命中词列表]
        - 'miss':    [缺失词列表]
        - 'rate':    float                   — 匹配率（0.0 ~ 1.0）
    """
    # 1. 简历全文统一变小写，后面比对时关键词也变小写，这样忽略大小写
    text_lower = resume_text.lower()

    # 2. 准备容器
    results = {}   # 存每个词的匹配结果
    hit = []       # 命中的关键词
    miss = []      # 缺失的关键词

    # 3. 遍历每个关键词，看它是否出现在简历里
    for kw in keywords:
        # kw.lower() 把关键词也变小写，两边统一就能对上
        if kw.lower() in text_lower:
            results[kw] = True
            hit.append(kw)
        else:
            results[kw] = False
            miss.append(kw)

    # 4. 算匹配率：命中数 / 总数
    total = len(keywords)
    rate = len(hit) / total if total > 0 else 0.0

    return {
        "results": results,
        "hit": hit,
        "miss": miss,
        "rate": rate,
    }
