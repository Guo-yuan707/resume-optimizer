"""网页入口(第 15 课重写):把简历优化工具做成一个清爽的网页应用。

运行方式(在项目根目录):
    streamlit run app.py

第 15 课改动一览:
    1. 布局:去掉左侧边栏 → 居中单栏,浅灰底 + 白底圆角卡片 + 靛蓝强调色
    2. 上传:简历支持 .txt/.pdf/.docx;JD 支持 .txt/.md/.jpg/.png(图片自动 OCR)
             也能直接粘贴文本 —— 一律先进 loader.extract_text() 变纯文本
    3. 去掉手动关键词框:关键词只来自 JD(上传/粘贴 → AI 提取 → 可确认删减)
    4. 未传 JD:醒目提醒 + 降级只跑质量检查;模型等参数收进折叠的"高级选项"

核心模块(parser/matcher/checker/llm/knowledge)仍然一行没改 ——
它们吃纯文本,新格式只在上传这一层被 loader 翻译成文本而已。
"""
import html

import streamlit as st

from resume_optimizer.loader import extract_text
from resume_optimizer.parser import parse_resume
from resume_optimizer.matcher import match_keywords
from resume_optimizer.checker import check_all
from resume_optimizer.llm import (
    extract_keywords_from_jd,
    get_optimization_advice,
    get_rewritten_resume,
)
from resume_optimizer.knowledge import build_knowledge_context

from config import MODELS, DEFAULT_MODEL, RESUME_ACCEPT, JD_ACCEPT

# ===== 页面基础配置(必须是第一个 Streamlit 命令)=====
st.set_page_config(
    page_title="简历优化助手",
    page_icon="📄",
    layout="centered",          # 居中单栏,内容宽度受控,观感更聚焦
)


def _inject_css() -> None:
    """注入自定义 CSS:把 Streamlit 默认样式改成"清爽浅色·专业"质感。

    色板:页面浅灰 #F4F5F7、卡片白 #FFF、文字深灰 #1F2937、强调靛蓝 #2563EB。
    卡片靠 .stVerticalBlockBorderWrapper(border=True 的容器)套白底圆角阴影。
    """
    st.markdown(
        """
        <style>
        /* 中文字体栈:Mac/Windows/Linux 各取合适的字体 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                         "Noto Sans SC", sans-serif;
        }

        /* 主区留白 */
        .block-container { padding-top: 2.2rem; padding-bottom: 3rem; }

        /* 白底圆角卡片(border=True 的容器) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF;
            border: 1px solid #EAECF0 !important;
            border-radius: 16px;
            box-shadow: 0 1px 2px rgba(16,24,40,0.04), 0 2px 10px rgba(16,24,40,0.05);
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div { padding: 0.1rem 0.4rem; }

        /* 标题去笨重感 */
        h1 { letter-spacing: -0.02em; color: #111827; }
        h4 { letter-spacing: -0.01em; color: #111827; margin-top: 0.2rem; }

        /* 主按钮:圆角 + 主色 */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
        }
        .stButton > button[kind="primary"] {
            background: #2563EB; border-color: #2563EB;
        }
        .stButton > button[kind="primary"]:hover {
            background: #1D4ED8; border-color: #1D4ED8;
        }

        /* 上传拖拽区:浅底 + 主色虚线,更像"拖进来" */
        [data-testid="stFileUploaderDropzone"] {
            background: #FBFCFE;
            border: 1px dashed #C7D2FE;
            border-radius: 12px;
        }

        /* 小节标题(结果区卡片里的分类名) */
        .sec-title {
            font-size: 1.05rem; font-weight: 650; color: #111827;
            margin: 0.2rem 0 0.3rem;
        }
        /* 小节下的灰色说明文字 */
        .sec-sub { font-size: 0.85rem; color: #6B7280; margin-bottom: 0.5rem; }

        /* 关键词 chip(小圆角标签):命中浅绿 / 缺失浅红 */
        .chip {
            display: inline-block; padding: 2px 10px; margin: 2px 4px 2px 0;
            border-radius: 999px; font-size: 0.82rem;
        }
        .chip-ok   { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
        .chip-miss { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }

        /* 步骤提示 */
        .step-hint { color: #6B7280; font-size: 0.9rem; }

        /* 藏掉 Streamlit 页脚/汉堡等杂项,页面更干净 */
        #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _chip(text: str, ok: bool) -> str:
    """把单个关键词渲染成一个"命中/缺失"的小标签(HTML span)。"""
    kind = "chip-ok" if ok else "chip-miss"
    return f'<span class="chip {kind}">{html.escape(text)}</span>'


def _read_upload(uploaded) -> str:
    """把 Streamlit 上传的文件交给 loader,抽成纯文本。失败抛带提示的错。"""
    return extract_text(uploaded.name, uploaded.getvalue())


def _render_quality_card(check_results: list[dict]) -> None:
    """质量检查卡片:过的浅绿、没过的浅红,一行一条(克制,不刷屏)。"""
    st.markdown('<div class="sec-title">简历质量检查</div>', unsafe_allow_html=True)
    for r in check_results:
        if r["pass"]:
            st.markdown(f'<div style="color:#047857;">✓ {html.escape(r["message"])}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:#B91C1C;">✗ {html.escape(r["message"])}</div>', unsafe_allow_html=True)
    passed = sum(1 for r in check_results if r["pass"])
    st.caption(f"通过 {passed}/{len(check_results)} 项")


def _no_jd_hint(jd_error: str = "") -> None:
    """JD 缺失/读取失败时的大号提醒(居中醒目)。"""
    lines = [
        "⚠️ **还没提供 JD** — 关键词匹配、岗位知识参考和 AI 改写都依赖 JD。",
        "当前仅为你展示【简历质量检查】;补传/粘贴 JD 后即可获得完整分析。",
    ]
    if jd_error:
        lines.append(f"\n> JD 读取提示:{jd_error}")
    st.warning("\n".join(lines))


# ===== 注入样式(每次重跑都执行,保证样式在)=====
_inject_css()

# ===== 页头 =====
st.markdown("# 📄 简历优化助手")
st.caption("上传简历与目标职位 JD → 关键词匹配 · 质量检查 · AI 改写建议(带岗位知识库)")

# ========== 输入卡:两个独立上传窗 ==========
with st.container(border=True):
    st.markdown('<div class="sec-sub">1. 简历</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "简历文件",
        type=RESUME_ACCEPT,
        label_visibility="collapsed",
        help="支持 .txt / .pdf(文字型)/ .docx",
    )

    st.markdown('<div class="sec-sub">2. 目标职位 JD(决定关键词从哪来)</div>', unsafe_allow_html=True)
    jd_mode = st.radio(
        "JD 来源",
        ["上传文件或图片", "粘贴文本"],
        horizontal=True,
        label_visibility="collapsed",
    )
    jd_file = None
    jd_paste = ""
    if jd_mode == "上传文件或图片":
        jd_file = st.file_uploader(
            "JD 文件",
            type=JD_ACCEPT,
            label_visibility="collapsed",
            help="支持 .txt / .md / .jpg / .png(图片自动 OCR 识别文字)",
        )
        st.caption("上传 .jpg/.png 截图会自动识别出里面的文字,无需手动输入。")
    else:
        jd_paste = st.text_area(
            "粘贴 JD 文本",
            height=140,
            label_visibility="collapsed",
            placeholder="把职位描述复制到这里…",
        )

    with st.expander("⚙️ 高级选项"):
        model = st.selectbox(
            "AI 模型",
            MODELS,
            index=MODELS.index(DEFAULT_MODEL),
            help="flash 快/便宜;pro 质量更高(导出整份改写建议用 pro)",
        )

    analyze_clicked = st.button("开始分析", type="primary", use_container_width=True)

# ========== 结果区 ==========
if not analyze_clicked:
    # 还没点按钮:给一个"空状态"提示,别让页面空荡荡
    st.markdown(
        '<div class="step-hint" style="text-align:center;padding:2.4rem 0">'
        "① 上传简历 → ② 上传/粘贴 JD → ③ 点「开始分析」"
        "</div>",
        unsafe_allow_html=True,
    )
else:
    # ===== 1. 读简历(三种格式都先进 loader)=====
    if resume_file is None:
        st.error("❌ 请先上传简历文件(.txt / .pdf / .docx)")
    else:
        try:
            resume_text = _read_upload(resume_file)
        except ValueError as e:
            st.error(f"❌ 简历读取失败:{e}")
        else:
            resume = parse_resume(resume_text)
            check_results = check_all(resume)

            # ===== 2. 读 JD(文件 / 图片 / 粘贴)→ 转文本 =====
            jd_text = ""
            jd_error = ""
            if jd_mode == "上传文件或图片":
                if jd_file is not None:
                    try:
                        jd_text = _read_upload(jd_file)
                    except ValueError as e:
                        jd_error = str(e)   # 记住提示,等会儿展示
            else:
                jd_text = jd_paste.strip()

            # ---- 有 JD:完整报告 ----
            if jd_text.strip():
                # (a) AI 从 JD 提取关键词(慢,包转圈 + try/except)
                with st.spinner("🤖 AI 正在从 JD 提取关键词…"):
                    try:
                        extracted = extract_keywords_from_jd(jd_text, model=model)
                    except Exception as e:
                        st.error(f"❌ AI 提取关键词失败:{e}")
                        extracted = []
                keywords = (
                    st.multiselect(
                        "AI 提取的关键词(可取消勾选不需要的)",
                        extracted,
                        default=extracted,
                    )
                    if extracted
                    else []
                )

                if not keywords:
                    st.error("❌ 没有可用的关键词:JD 未能提取出关键词,请换一份 JD 或改粘贴文本")
                else:
                    # (b) 关键词匹配 + 质量检查
                    match_result = match_keywords(resume_text, keywords)
                    rate = match_result["rate"]

                    with st.container(border=True):
                        st.markdown('<div class="sec-title">🎯 关键词匹配</div>', unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="sec-sub">匹配率 <b style="color:#2563EB">{rate:.0%}</b>'
                            f"（{len(match_result['hit'])}/{len(keywords)}）</div>",
                            unsafe_allow_html=True,
                        )
                        st.progress(rate)
                        hit_html = "".join(_chip(k, True) for k in match_result["hit"])
                        miss_html = "".join(_chip(k, False) for k in match_result["miss"])
                        st.markdown(
                            f'<div style="margin-top:0.4rem">{hit_html}{miss_html}</div>',
                            unsafe_allow_html=True,
                        )

                    with st.container(border=True):
                        _render_quality_card(check_results)

                    # (c) 第 12 课:岗位知识库检索(有 JD 才检索)
                    knowledge_context = ""
                    with st.spinner("📚 正在从岗位知识库检索相关内容…"):
                        try:
                            knowledge_context = build_knowledge_context(jd_text)
                        except Exception as e:
                            st.warning(f"⚠️ 知识库检索失败(不影响后续分析):{e}")
                    if knowledge_context:
                        with st.expander("📚 AI 参考的岗位知识(从知识库检索到的)"):
                            st.text(knowledge_context)

                    # (d) AI 优化建议
                    with st.container(border=True):
                        st.markdown('<div class="sec-title">🤖 AI 优化建议</div>', unsafe_allow_html=True)
                        with st.spinner("AI 正在分析,请稍候…"):
                            try:
                                advice = get_optimization_advice(
                                    resume_text,
                                    match_result,
                                    check_results,
                                    model=model,
                                    knowledge_context=knowledge_context,
                                )
                                st.markdown(advice)
                            except Exception as e:
                                st.error(f"❌ 调用 AI 失败:{e}")

                    # (e) 导出整份改写(第 9 课)
                    with st.container(border=True):
                        st.markdown('<div class="sec-title">⬇️ 导出优化版简历</div>', unsafe_allow_html=True)
                        with st.spinner("AI 正在改写整份简历…"):
                            try:
                                rewritten = get_rewritten_resume(
                                    resume_text,
                                    match_result,
                                    check_results,
                                    model=model,
                                    knowledge_context=knowledge_context,
                                )
                                st.download_button(
                                    "📥 下载优化版简历",
                                    data=rewritten,
                                    file_name="optimized_resume.txt",
                                    mime="text/plain",
                                )
                            except Exception as e:
                                st.error(f"❌ 导出失败:{e}")
            else:
                # ---- 无 JD:醒目提醒 + 降级只跑质量检查 ----
                _no_jd_hint(jd_error)
                with st.container(border=True):
                    _render_quality_card(check_results)
