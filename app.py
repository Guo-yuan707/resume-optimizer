"""网页入口(第 6 课):用 Streamlit 把简历优化工具搬到浏览器里。

运行方式(在项目根目录):
    streamlit run app.py

页面结构:
    左侧边栏 = 输入区(上传简历、填关键词、选模型、点按钮)
    主区域   = 输出区(匹配结果、质量检查、AI 建议)

关键思路:第 1~5 课的 4 个模块(parser/matcher/checker/llm)一行不改,
    网页只是换了"外壳"——把它们的返回结果用 st.xxx 显示出来。
"""
import streamlit as st

from resume_optimizer.parser import parse_resume
from resume_optimizer.matcher import match_keywords
from resume_optimizer.checker import check_all
from resume_optimizer.llm import get_optimization_advice, extract_keywords_from_jd, get_rewritten_resume
from resume_optimizer.knowledge import build_knowledge_context

from config import MODELS, DEFAULT_MODEL

# ========== 页面顶部 ==========
st.title("📄 简历优化助手")
st.caption("上传简历 + 填 JD 关键词 → 匹配分析、质量检查、AI 改写建议")

# ========== 左侧边栏:输入区 ==========
st.sidebar.header("🎛️ 输入")

# 文件上传控件:type=["txt"] 表示只接受 .txt 文件
uploaded = st.sidebar.file_uploader("1️⃣ 上传简历(.txt)", type=["txt"])

# JD 两种来源:上传文件 或 粘贴文本(第 8 课新增)
jd_file = st.sidebar.file_uploader("2️⃣ 上传 JD 文本(.txt/.md)", type=["txt", "md"])
jd_paste = st.sidebar.text_area(
    "或粘贴 JD 文本(和上传二选一)",
    placeholder="把职位描述复制到这里…",
)

# 手动关键词:作为 JD 的兜底(没传 JD 时才用)
keywords_str = st.sidebar.text_input(
    "手动关键词(英文逗号分隔,可选)",
    placeholder="例如:Python, API, Git, LLM",
)

# 下拉选择框:选模型(可选列表来自 config.py,默认值也用 config 的)
model = st.sidebar.selectbox(
    "3️⃣ 选择模型",
    MODELS,
    index=MODELS.index(DEFAULT_MODEL),
)

# 按钮:点了才执行下面的分析(返回 True/False)
analyze_clicked = st.sidebar.button("开始分析", type="primary")

# ========== 主区域:输出区 ==========
if not analyze_clicked:
    # 还没点按钮:只显示提示
    st.info("👈 在左侧上传简历、填好关键词,点「开始分析」")
else:
    # 点了按钮:先校验输入,再跑分析
    if uploaded is None:
        st.error("❌ 请先上传简历文件(.txt)")
    else:
        # 1. 读上传的简历:它在内存里,直接读字节 → 解码成 UTF-8 中文文本
        text = uploaded.read().decode("utf-8")

        # 2. 解析成结构化数据(第 2 课)
        resume = parse_resume(text)

        # ---- 第 8 课:确定关键词来源 ----
        # 优先:JD 上传/粘贴 → AI 自动提取;没有 JD 才用手动关键词
        if jd_file is not None:
            jd_text = jd_file.read().decode("utf-8")
        elif jd_paste.strip():
            jd_text = jd_paste.strip()
        else:
            jd_text = ""

        if jd_text:
            # AI 自动提取关键词(慢,包转圈;AI 可能失败,包 try/except)
            st.subheader("🤖 自动提取 JD 关键词")
            with st.spinner("AI 正在分析 JD,提取关键词…"):
                try:
                    extracted = extract_keywords_from_jd(jd_text, model=model)
                except Exception as e:
                    st.error(f"❌ AI 提取关键词失败:{e}")
                    extracted = []
            # 让用户确认/删减 AI 提取的关键词
            keywords = (
                st.multiselect(
                    "AI 提取的关键词(可取消勾选不需要的)",
                    extracted,
                    default=extracted,
                )
                if extracted
                else []
            )
        else:
            # 手动关键词兜底:把 "Python, API, Git" 切成 ["Python", "API", "Git"]
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

        if not keywords:
            st.error("❌ 没有可用的关键词:请上传 JD 让 AI 提取,或手动填写关键词")
        else:
            # 3. 关键词匹配(第 3 课)
            match_result = match_keywords(text, keywords)

            # 4. 质量检查(第 4 课)
            check_results = check_all(resume)

            # ----- 显示:关键词匹配 -----
            st.subheader("🎯 关键词匹配")
            rate = match_result["rate"]
            st.progress(rate, text=f"匹配率 {rate:.0%}")
            for kw in keywords:
                if match_result["results"][kw]:
                    st.success(f"✅ {kw}")
                else:
                    st.error(f"❌ {kw}")

            # ----- 显示:质量检查 -----
            st.subheader("🔍 简历质量检查")
            for r in check_results:
                if r["pass"]:
                    st.success(r["message"])
                else:
                    st.error(r["message"])

            # ----- 第 12 课:从岗位知识库检索相关内容(有 JD 才检索)-----
            knowledge_context = ""
            if jd_text:
                with st.spinner("📚 正在从岗位知识库检索相关内容…"):
                    try:
                        knowledge_context = build_knowledge_context(jd_text)
                    except Exception as e:
                        st.warning(f"⚠️ 知识库检索失败(不影响后续分析):{e}")
                if knowledge_context:
                    with st.expander("📚 AI 参考的岗位知识(从知识库检索到的)"):
                        st.text(knowledge_context)

            # ----- 显示:AI 优化建议(最慢,包转圈 + try/except)-----
            st.subheader("🤖 AI 优化建议")
            with st.spinner("AI 正在分析,请稍候…"):
                try:
                    advice = get_optimization_advice(
                        text,
                        match_result,
                        check_results,
                        model=model,
                        knowledge_context=knowledge_context,
                    )
                    st.markdown(advice)
                except Exception as e:
                    st.error(f"❌ 调用 AI 失败:{e}")

            # ----- 第 9 课:导出优化版简历(可下载)-----
            st.subheader("⬇️ 导出优化版简历")
            with st.spinner("AI 正在改写整份简历…"):
                try:
                    # 让 AI 输出一整份改写后的简历,模型跟着用户在侧边栏选的走
                    # 第 12 课起带上岗位知识参考:AI 改写时贴合真实岗位要求
                    rewritten = get_rewritten_resume(
                        text,
                        match_result,
                        check_results,
                        model=model,
                        knowledge_context=knowledge_context,
                    )
                    # 点按钮直接在浏览器里下载,不用先存服务器磁盘
                    st.download_button(
                        "📥 下载优化版简历 (.txt)",
                        data=rewritten,
                        file_name="optimized_resume.txt",
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"❌ 导出失败:{e}")
