"""测试 retriever.py 的纯逻辑部分:dot_product / vector_norm / cosine_similarity。

检索流程(build_knowledge_index + retrieve)需要 TF-IDF 向量化,
虽不联网但也依赖 sklearn,暂不测。只测三个纯数学函数。
"""

from pytest import approx

from resume_optimizer.retriever import cosine_similarity, dot_product, vector_norm


# ─── dot_product ──────────────────────────────────────────────

def test_dot_product_positive():
    """两个正数向量,点积是对应相乘再求和。"""
    a = [1.0, 3.0, -5.0]
    b = [4.0, -2.0, -1.0]
    # 1×4 + 3×(-2) + (-5)×(-1) = 4 + (-6) + 5 = 3
    assert dot_product(a, b) == 3.0


def test_dot_product_identical():
    """两个相同向量,点积等于各分量平方和。"""
    a = [2.0, 2.0, 2.0]
    assert dot_product(a, a) == 12.0  # 4 + 4 + 4


def test_dot_product_orthogonal():
    """垂直的向量(对应位置一个为 0),点积为 0。"""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert dot_product(a, b) == 0.0


# ─── vector_norm ──────────────────────────────────────────────

def test_vector_norm_unit():
    """单位向量 [1,0,0] 的长是 1。"""
    assert vector_norm([1.0, 0.0, 0.0]) == 1.0


def test_vector_norm_345():
    """3-4-5 直角三角形:sqrt(9+16)=5。"""
    assert vector_norm([3.0, 4.0]) == 5.0


# ─── cosine_similarity ────────────────────────────────────────

def test_cosine_identical():
    """相同方向的向量,余弦相似度为 1。"""
    a = [1.0, 2.0, 3.0]
    assert cosine_similarity(a, a) == 1.0


def test_cosine_orthogonal():
    """垂直向量,余弦相似度为 0。"""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == 0.0


def test_cosine_opposite():
    """完全相反的方向,余弦相似度为 -1。"""
    a = [1.0, 2.0]
    b = [-1.0, -2.0]
    # 浮点数有精度误差,-0.9999999999999998 ≈ -1.0,用 approx 比较
    assert cosine_similarity(a, b) == approx(-1.0)


def test_cosine_zero_vector():
    """零向量没有方向,相似度返回 0.0 而不是崩溃。"""
    a = [0.0, 0.0, 0.0]
    b = [1.0, 2.0, 3.0]
    assert cosine_similarity(a, b) == 0.0
    assert cosine_similarity(b, a) == 0.0  # 对称也安全
