"""项目入口:读取简历文件,解析成结构化数据,按段落打印+关键词匹配。

运行方式(在项目根目录):
    python main.py
"""
import sys

from resume_optimizer.parser import read_text, parse_resume
from resume_optimizer.matcher import match_keywords
from resume_optimizer.checker import check_all
from resume_optimizer.llm import get_optimization_advice, get_rewritten_resume
from resume_optimizer.exporter import save_resume
from resume_optimizer.knowledge import build_knowledge_context

from config import DEFAULT_RESUME_PATH, DEFAULT_JD_PATH, DEFAULT_JD_KEYWORDS, OUTPUT_PATH


def fix_console_encoding():
    """把输出编码强制设为 UTF-8,解决 Windows 下中文乱码。

    原因:Windows 的 Python 默认用系统编码(GBK)往终端写中文,
    而现代终端默认按 UTF-8 显示,两边不一致就乱码了。
    """
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    # 0. 先解决 Windows 中文乱码问题
    fix_console_encoding()

    # 1. 读进简历文本
    resume_path = DEFAULT_RESUME_PATH
    text = read_text(resume_path)

    # 2. 解析成结构化数据(Resume 对象)
    resume = parse_resume(text)

    # 3. 按段落打印
    print("=" * 50)
    print("基本信息")
    print("=" * 50)
    for line in resume.header:
        print(line)

    print("\n" + "=" * 50)
    print("专业技能")
    print("=" * 50)
    for line in resume.skills:
        print(line)

    print("\n" + "=" * 50)
    print("教育经历")
    print("=" * 50)
    for line in resume.education:
        print(line)

    print("\n" + "=" * 50)
    print("项目经历")
    print("=" * 50)
    for line in resume.projects:
        print(line)

    print("\n" + "=" * 50)
    print("个人优势")
    print("=" * 50)
    for line in resume.strengths:
        print(line)

    # === 第 3 课新增：关键词匹配 ===
    # 模拟一份 JD（职位描述）的关键词列表。
    # 实际使用时可以从 JD 文件里提取，这里先用 config 里的默认值演示。
    jd_keywords = DEFAULT_JD_KEYWORDS

    print("\n" + "=" * 50)
    print("JD 关键词匹配(第 3 课)")
    print("=" * 50)
    print(f"JD 关键词列表: {jd_keywords}")
    print()

    # 调用匹配函数：把整份简历文本和关键词列表传进去
    match_result = match_keywords(text, jd_keywords)

    # 打印每个词的匹配结果
    for kw in jd_keywords:
        is_hit = match_result["results"][kw]
        mark = "✅" if is_hit else "❌"
        print(f"  {mark} {kw}")

    # 打印汇总
    print()
    print(f"命中: {match_result['hit']}")
    print(f"缺失: {match_result['miss']}")
    print(f"匹配率: {match_result['rate']:.0%}  ({len(match_result['hit'])}/{len(jd_keywords)})")

    # === 第 4 课新增：简历质量检查 ===
    print("\n" + "=" * 50)
    print("简历质量检查（第 4 课）")
    print("=" * 50)

    check_results = check_all(resume)

    for r in check_results:
        # 过的用绿色 ✅，不过的用红色 ❌
        print(f"  {r['message']}")

    # 统计：几条通过、几条不通过
    passed = sum(1 for r in check_results if r["pass"])
    failed = sum(1 for r in check_results if not r["pass"])
    print()
    print(f"通过 {passed} 项，未通过 {failed} 项（共 {len(check_results)} 项检查）")

    # === 第 12 课新增：RAG 检索岗位知识 ===
    # 拿 JD 去知识库检索最相关的几段岗位要求，喂给 AI 当"开卷考试"的参考书
    print("\n" + "=" * 50)
    print("岗位知识检索（第 12 课，RAG）")
    print("=" * 50)

    knowledge_context = ""
    try:
        jd_text = read_text(DEFAULT_JD_PATH)
        knowledge_context = build_knowledge_context(jd_text)
        if knowledge_context:
            print(f"✅ 从知识库检索到最相关的岗位要求：\n{knowledge_context}")
        else:
            print("⚠️ 知识库为空或没检索到相关内容，AI 将不带参考。")
    except Exception as e:
        print(f"⚠️ 知识库检索失败（不影响后续）：{e}")

    # === 第 5 课新增：调用大模型生成优化建议 ===
    print("\n" + "=" * 50)
    print("AI 优化建议（第 5 课）")
    print("=" * 50)

    try:
        # 把简历原文、匹配结果、检查结果一起发给 DeepSeek（第 12 课起，带上岗位知识参考）
        advice = get_optimization_advice(
            text, match_result, check_results, knowledge_context=knowledge_context
        )
        print(advice)
    except Exception as e:
        # 网络断了 / Key 错了 / 额度用完了……都不会让程序崩溃
        print(f"❌ 调用 AI 失败：{e}")
        print("请检查：① .env 里 API Key 是否正确 ② 网络是否通畅 ③ DeepSeek 账户是否有余额")

    # === 第 9 课新增：导出优化版简历 ===
    print("\n" + "=" * 50)
    print("导出优化版简历（第 9 课）")
    print("=" * 50)

    try:
        # 让 AI 输出一整份改写后的简历(默认用 pro 模型,质量更高)
        # 第 12 课起带上岗位知识参考:AI 改写时贴合真实岗位要求
        rewritten = get_rewritten_resume(
            text, match_result, check_results, knowledge_context=knowledge_context
        )
        # 把改写结果写进文件
        save_path = save_resume(rewritten, OUTPUT_PATH)
        print(f"✅ 已保存优化版简历到: {save_path}")
        print("打开文件检查内容,不满意可以再跑一次让 AI 重新改。")
    except Exception as e:
        print(f"❌ 导出失败：{e}")
        print("提示:导出依赖 AI 调用成功,如果刚才的 AI 建议也失败了,多半是网络/Key/额度问题。")


# 只有「直接运行本文件」时才会执行 main();
# 被其他文件 import 时不会执行,保证模块可以被复用
if __name__ == "__main__":
    main()
