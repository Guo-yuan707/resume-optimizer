"""知识库模块(第 10 课):读取岗位文档 + 把长文本切块。

RAG 的第一步:准备好"资料"(知识库),并把资料切成小块,
这样第 11 课做相似度检索时,才能精确找到"最相关的那一小块"。

三个核心函数:
    1. read_knowledge_files()    读 examples/knowledge/ 下所有文档
    2. chunk_text()              把一段长文本切成小块
    3. build_knowledge_context() 拿 JD 检索知识库,拼成参考段落(第 12 课)

知识库 = 一摞真实的岗位要求文档。示例先放了 3 份,
以后可以把你在 BOSS 上投的那些真实 JD 都丢进 examples/knowledge/。
"""
import os

from resume_optimizer.retriever import build_knowledge_index, retrieve


# 知识库目录:固定放在项目根的 examples/knowledge/
# 用 os.path 拼路径,保证在 Windows 上也能正确找到
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "examples", "knowledge")


def read_knowledge_files() -> list[str]:
    """读取知识库目录下所有 .txt 文档,返回文档内容列表。

    返回:
        list[str]: 每份文档的全文(去掉首尾空白)。目录不存在或为空时返回空列表。
    """
    # 把相对路径变成绝对路径:../examples/knowledge → d:/Project/.../examples/knowledge
    knowledge_dir = os.path.abspath(KNOWLEDGE_DIR)

    docs: list[str] = []
    if not os.path.isdir(knowledge_dir):
        return docs

    # os.listdir:列出目录下所有文件名;.txt 结尾的才收进来
    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(knowledge_dir, filename)
            with open(filepath, encoding="utf-8") as f:
                docs.append(f.read().strip())

    return docs


def chunk_text(text: str, chunk_size: int = 100) -> list[str]:
    """把一段长文本切成小块,返回块列表。

    策略(按"内容边界"切,而不是按字数硬切):
        1. 按空行把文本拆成若干段落
        2. 每个段落里的每一行,若长度 > chunk_size 就继续切小;
           否则一整行就是一块

    参数:
        text:       要切的原文
        chunk_size: 每块大约多少字符(默认 100,一行岗位要求通常 30~60 字)

    返回:
        非空块的列表,顺序保持原文顺序。
    """
    # 1. 按空行拆段落:连续换行 "·" 用 split("\n\n") 拆
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    for para in paragraphs:
        # 2. 段落内按行拆:一行一行处理
        for line in para.split("\n"):
            line = line.strip()
            if not line:
                continue
            # 3. 一行太长 → 按标点切成小块;短 → 一整行就是一块
            chunks.extend(_split_long_line(line, chunk_size))

    return chunks


def _split_long_line(line: str, chunk_size: int) -> list[str]:
    """把一行切成不超过 chunk_size 的多块(内部函数,以 _ 开头,别从外部 import)。

    思路:从行首开始,切出一段字符;如果这段字符里正好有逗号/句号,
    就停在最后一个标点处(保留语义);没有标点就硬切。

    参数:
        line:       单行文本 
        chunk_size: 每块最大字符数

    返回:
        切好的一行多块(可能只有一块)。
    """
    if len(line) <= chunk_size:
        return [line]

    pieces: list[str] = []
    remaining = line
    while len(remaining) > chunk_size:
        # 在前 chunk_size 个字符里,找最后一个中文标点(，。、；)的位置
        cut = chunk_size
        for punct in "，。、；":
            idx = remaining.rfind(punct, 0, chunk_size)
            if idx != -1:
                # 找到标点,就把这标点后面的字也算进来一起切(避免把标点丢掉)
                cut = max(cut, idx + 1)
        # 取开头到 cut 这一块,剩下的继续循环
        piece = remaining[:cut]
        pieces.append(piece)
        remaining = remaining[cut:].strip()

    if remaining:
        pieces.append(remaining)
    return pieces


def build_knowledge_context(jd_text: str, top_k: int = 3) -> str:
    """拿 JD 去知识库检索,拼成一段可写进 prompt 的岗位知识参考(第 12 课)。

    这就是 RAG 的「检索 + 增强」两步一条龙——把第 10、11 课攒的零件串起来:
        1. 读知识库所有文档 → 切成小块(本文件的 read_knowledge_files + chunk_text)
        2. 建 TF-IDF 索引 → 拿 JD 检索最相关的 top_k 块(retriever.py 的两个函数)
        3. 把检索到的块拼成一段编号文字返回

    返回空字符串 = 没有参考(知识库为空 / 检索不到),上层就当"没带参考"处理,
    llm.py 的 build_prompt / build_rewrite_prompt 接到空串就不拼那一段。

    生活例子:资料员接到问题(JD),从档案柜(知识库)抽出最相关的 3 张卡片,
    抄成一张编号便签给你——这张便签就是给 AI 看的"岗位知识参考"。

    参数:
        jd_text: 职位描述(用户上传/粘贴的 JD)
        top_k:   取最相关的几块,默认 3

    返回:
        一段可直接拼进 prompt 的编号文本;知识库为空时返回 ""。
    """
    # 1. 读知识库所有文档 + 全部切块(第 10 课)
    all_chunks: list[str] = []
    for doc in read_knowledge_files():
        all_chunks.extend(chunk_text(doc))

    if not all_chunks:
        return ""

    # 2. 建索引 + 用 JD 检索最相关的 top_k 块(第 11 课)
    index = build_knowledge_index(all_chunks)
    results = retrieve(jd_text, index, top_k=top_k)

    if not results:
        return ""

    # 3. 拼成编号段落:enumerate(results, start=1) → (1, 第1条), (2, 第2条)...
    lines = [f"{i}. {item['text']}" for i, item in enumerate(results, start=1)]
    return "\n".join(lines)
