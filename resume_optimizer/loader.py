"""文件读取模块(第 15 课新增):把「用户上传的各种文件」统一变成纯文本。

第 15 课之前,网页版只收 .txt,简历也只能先转成文本再传,很麻烦。
这一课扩展支持的格式:
    简历  — .txt / .pdf(文字型)/ .docx
    JD    — .txt / .md / .jpg / .png(图片自动 OCR 识别文字)

为什么单独建一个模块?因为解析(parser)、匹配(matcher)、检查(checker)、
LLM(llm)、知识库(knowledge)全都只认「纯文本字符串」。所以让这里负责
"不管什么格式,都先翻译成纯文本",下游一个字符都不用改。

关键设计(面试可讲):
    1. 按文件扩展名分发 → 每种格式一个专用小函数,好加好测
    2. 吃内存字节(Streamlit 上传的文件在内存里,.getvalue() 拿字节),
       不落盘,干净又安全
    3. 重依赖(pdf/docx/OCR 库)全部放函数内 import —— 懒加载:
       只用某格式时才加载对应库,模块 import 本身永远轻快;
       即使 OCR 库没装,其余功能照常能用
"""
import os
import tempfile
from io import BytesIO


def extract_text(filename: str, data: bytes) -> str:
    """把上传文件的内容抽成纯文本(第 15 课主入口)。

    参数:
        filename: 文件名,用来判断格式(例如 "简历.pdf")
        data:     文件的原始字节(Streamlit: uploaded.getvalue())

    返回:
        文件里的全部文字

    抛错:
        ValueError —— 不认识的文件格式 / 图片型(扫描版)PDF / OCR 不可用,
                     给用户看的是"怎么修"而不是一串吓人的堆栈
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # 查表:扩展名 → 对应读取函数(表在文件底部定义,值就是函数本身)
    reader = _EXT_TO_READER.get(ext)
    if reader is None:
        supported = "、".join(f".{e}" for e in sorted(set(_EXT_TO_READER)))
        raise ValueError(
            f"不支持的文件格式 .{ext}\n目前支持:{supported}\n"
            "简历请用 .txt/.pdf/.docx;JD 请用 .txt/.md/.jpg/.png"
        )

    return reader(data)


# ---------- .txt / .md:纯文本 ----------

def _read_txt(data: bytes) -> str:
    """读纯文本。先按 utf-8 解,失败就退到 gb18030。

    为什么要兜底?Windows 记事本另存的 txt 常见是 GBK/GB18030 编码,
    中文用 utf-8 直接解会抛 UnicodeDecodeError。gb18030 是 GBK 的超集,
    兜底这一手能覆盖绝大多数"打不开的中文 txt"。
    """
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        # 试 gb18030;再失败就抛给上层,让用户知道是编码问题
        return data.decode("gb18030")


# ---------- .pdf:文字型 PDF ----------

def _read_pdf(data: bytes) -> str:
    """读文字型 PDF:逐页抽出可选中的文字,拼成一段文本。

    只能处理"文字型"PDF(文字能选中/复制的那种)。
    扫描版 PDF(整页是图片)抽不出字 —— 那属于 OCR 的活,这里如实报错。
    """
    # 懒加载:pypdf 只在真要读 PDF 时才 import,加快模块启动
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")

    text = "\n".join(pages_text).strip()
    if not text:
        raise ValueError(
            "这份 PDF 里没有可提取的文字,可能是扫描版(整页是图片)简历。\n"
            "请改用文字版 PDF(如 Word 另存为 PDF),或直接上传 .docx。"
        )
    return text


# ---------- .docx:Word 文档 ----------

def _read_docx(data: bytes) -> str:
    """读 Word .docx:段落 + 表格都读,按文档顺序拼成文本。

    为什么连表格也读?很多简历正文是放在表格里排版的(一行一段),
    只读段落(paragraphs)会漏掉大段内容。
    """
    # 懒加载:python-docx 在函数内 import
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(BytesIO(data))

    # doc.element.body 是文档的"骨架",按顺序遍历它,才能拿到
    # 「段落 → 表格 → 段落」的真实先后顺序,而不是把段落和表格各读各的
    parts = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):          # 一个段落
            parts.append(Paragraph(child, doc).text)
        elif child.tag == qn("w:tbl"):      # 一个表格:逐行逐格读
            table = Table(child, doc)
            for row in table.rows:
                for cell in row.cells:
                    parts.append(cell.text)

    return "\n".join(p for p in parts if p.strip())


# ---------- .jpg / .png:图片,靠 OCR 认字 ----------

# OCR 引擎很"重"(首次加载模型要几秒),所以做成模块级缓存:
# 一个会话内只初始化一次,第二次识别就直接复用,不用再等
_ocr_engine = None


def _get_ocr_engine():
    """拿到(并缓存)OCR 引擎。第一次调用才真正加载模型。

    双 import 兼容:
        rapidocr-onnxruntime 是老包名(自带中英文模型,本项目用的它);
        rapidocr 是新版统一包名。哪个装得上就用哪个,代码不用改。
    """
    global _ocr_engine
    if _ocr_engine is not None:
        return _ocr_engine

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        try:
            from rapidocr import RapidOCR
        except ImportError:
            raise ValueError(
                "图片识别(OCR)库未安装,暂时无法识别 .jpg/.png 的 JD。\n"
                "请用 .venv/Scripts/pip install rapidocr-onnxruntime 安装后重试。"
            )

    # 真正初始化模型(首次会慢几秒是正常的);失败给友好提示
    try:
        _ocr_engine = RapidOCR()
    except Exception as e:
        raise ValueError(f"OCR 模型加载失败:{e}\n可尝试重装 rapidocr-onnxruntime。")
    return _ocr_engine


def _read_image(data: bytes) -> str:
    """用 OCR 识别图片里的文字,按识别出的每行文本返回。

    识别结果是一串带坐标的框 [框, 文字, 置信度],我们只取中间的「文字」,
    按从上到下的顺序拼起来(RapidOCR 已按阅读顺序返回)。
    """
    engine = _get_ocr_engine()

    # RapidOCR 最稳的喂法是把字节先写成临时文件,再把路径交给它;
    # 用 NamedTemporaryFile 保证用完即删,不污染磁盘
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    try:
        tmp.write(data)
        tmp.close()

        result, _ = engine(tmp.name)   # (识别结果, 耗时),耗时我们不要
        if not result:
            return ""
        lines = [item[1] for item in result if len(item) > 1 and item[1]]
        return "\n".join(lines)
    finally:
        # 无论成功失败,临时文件都要删掉
        tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


# ---------- 分发表:扩展名 → 对应的读取函数(放在函数定义之后) ----------
_EXT_TO_READER = {
    "txt": _read_txt,
    "md": _read_txt,        # markdown 本质也是纯文本
    "pdf": _read_pdf,
    "docx": _read_docx,
    "jpg": _read_image,
    "jpeg": _read_image,
    "png": _read_image,
}
