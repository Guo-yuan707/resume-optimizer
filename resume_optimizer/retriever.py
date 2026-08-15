"""检索模块(第 11 课):把知识库文本向量化 + 用余弦相似度检索最相关块。

RAG 三步:检索 → 增强 → 生成。本模块管第一步「检索」:
    1. 把知识库里所有块转成 TF-IDF 向量(一堆数字)
    2. 把用户的查询也转成向量
    3. 算余弦相似度,找出和查询最相关的 top_k 块

三大核心函数:
    - cosine_similarity(vec_a, vec_b)         计算两个向量的余弦相似度
    - build_knowledge_index(chunks)           把知识库块"索引化"(拟合 TF-IDF + 向量化)
    - retrieve(query, index, top_k=5)         根据查询从索引中检索最相关块

所有计算纯本地、不调 API、不花钱。TF-IDF 只是入门向量化,
以后学到 embedding 模型(第 12 课)可以换更强的。
"""

import math

from sklearn.feature_extraction.text import TfidfVectorizer


# ────────────────────────────── 第一关:余弦相似度 ──────────────────────────────

def dot_product(a: list[float], b: list[float]) -> float:
    """计算两个向量的点积:对应位置相乘再求和(点积 = 余弦相似度的分子)。

    例子:
        a = [1.0, 3.0, -5.0]
        b = [4.0, -2.0, -1.0]
        dot = 1×4 + 3×(-2) + (-5)×(-1) = 4 + (-6) + 5 = 3

    生活例子:两个人购物篮的"重合程度"——A 买了 2 个苹果 1 瓶水,
    B 买了 1 个苹果 2 瓶水,对应位置乘起来再求和,数字越大越像。
    """
    total = 0.0
    for x, y in zip(a, b):
        total += x * y
    return total


def vector_norm(vec: list[float]) -> float:
    """计算向量的长度(也叫模 L2 norm):每个分量的平方求和再开根号。

    例子:vec = [3.0, 4.0], length = sqrt(9 + 16) = sqrt(25) = 5.0

    生活例子:直角三角形斜边长——长边 3、短边 4,斜边就是 5。
    """
    return math.sqrt(sum(x * x for x in vec))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度,范围 [-1, 1],越大越相似。

    公式:cos(θ) = (A·B) / (|A| × |B|)

    分子是点积,分母是两个向量长度的乘积。分母为 0 时返回 0.0(零向量没有方向,无法比较)。

    生活例子:两个人往同一个方向走 → 余弦值接近 1;各走各的 → 接近 0。
    """
    dot = dot_product(a, b)
    norm_a = vector_norm(a)
    norm_b = vector_norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


# ────────────────────────────── 第二关:向量化 + 索引 ──────────────────────────────

def build_knowledge_index(chunks: list[str]) -> dict:
    """把知识库块列表变成「索引」:一份随时可检索的数据结构。

    所谓「索引」就是把所有块一次性 TF-IDF 向量化,存成一个字典(dict),
    里面三个关键部分:

        - chunks:       原始块文本列表(搜到了要原样返回给人看)
        - matrix:       向量矩阵,每一行 = 一个块的 TF-IDF 向量
        - vectorizer:   TF-IDF 向量化器(搜的时候要把查询也按同一套词汇表转)

    TF-IDF 原理(本课讲过的概念,代码里怎么体现):
        - TF(词频):这个词在这段里出现几次——TfidfVectorizer 默认内部统计
        - IDF(逆文档频率):整个知识库里有几篇提到了这个词——vectorizer 拟合时算好
        - 最终每块转成的向量里,每个位置 = 一个词的 TF × IDF,重要词权重高。

    生活例子:期末考试前,把所有笔记按知识点整理成索引卡片——
    每张卡片正面是知识点(块文本),背面是一串关键词权重(向量)。
    考试时看到题目,你做的第一件事就是"查索引卡片,找最相关的几张"。
    """
    if not chunks:
        return {"chunks": [], "matrix": None, "vectorizer": None}

    # TF-IDF 向量化器:中文按单个字切(token_pattern 默认按字母切,中文得按字切)
    # analyzer="char" → 把一段中文拆成一个个汉字;ngram_range=(1,3) → 单字+双字+三字组合
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(1, 3))

    # fit_transform:先"学"(fit)整个知识库有哪些字和组合,再"转"(transform)成向量矩阵
    # 返回的是一个稀疏矩阵(很多 0,因为一份文档只会出现全部词汇的一小部分)
    matrix = vectorizer.fit_transform(chunks)

    return {
        "chunks": chunks,
        "matrix": matrix,
        "vectorizer": vectorizer,
    }


# ────────────────────────────── 第三关:检索 ──────────────────────────────

def retrieve(query: str, index: dict, top_k: int = 5) -> list[dict]:
    """根据查询从知识库索引中检索最相关的 top_k 块。

    检索三步:
        1. 把查询文本用同一套 vectorizer 转成向量
        2. 跟索引里每一块的向量逐个算余弦相似度
        3. 按相似度从高到低排序,取前 top_k 个,返回 {块文本, 相似度分数}

    参数:
        query:  用户输入,比如岗位 JD 的一段描述
        index:  build_knowledge_index() 返回的索引字典
        top_k:  返回最相似的几块,默认 5

    返回:
        [{"text": "块内容", "score": 0.85}, ...], 按 score 降序。
    """
    chunks = index["chunks"]
    matrix = index["matrix"]
    vectorizer = index["vectorizer"]

    if not chunks or matrix is None or vectorizer is None:
        return []

    # 1. 把查询文本转成向量(跟建索引用同一个 vectorizer,保证词汇表一致)
    query_vec = vectorizer.transform([query])

    # 2. 查询向量 vs 知识库每一块的向量 → 逐个算余弦相似度
    # matrix 的每一行是一个块的向量,query_vec 只有一行
    # 用一个循环:取出 matrix 第 i 行转成列表,跟 query_vec 的第一行算余弦
    scores: list[tuple[int, float]] = []
    q_dense = query_vec.toarray()[0].tolist()  # 查询向量(稠密列表)

    for i in range(matrix.shape[0]):
        doc_dense = matrix[i].toarray()[0].tolist()  # 第 i 块的向量
        sim = cosine_similarity(q_dense, doc_dense)
        scores.append((i, sim))

    # 3. 按相似度降序排序,取前 top_k
    scores.sort(key=lambda pair: pair[1], reverse=True)
    top = scores[:top_k]

    # 4. 组装返回结果
    results: list[dict] = []
    for idx, score in top:
        results.append({"text": chunks[idx], "score": round(score, 4)})

    return results
