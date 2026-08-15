"""集中配置(第 7 课):项目里所有"可调参数"都放在这里。

为什么要有这个文件?
    以前模型名、温度、简历路径、关键词散落在 main.py / app.py / llm.py 里,
    想改一个参数要到处搜。现在集中到一张"参数总表",改一处,全局生效。

用法:
    其他文件顶部写 `from config import 常量名`,就能直接用。
    注意:config.py 放在项目根目录,运行时也要在根目录执行
    (python main.py / streamlit run app.py 都满足)。
"""

# ===== 文件路径 =====
DEFAULT_RESUME_PATH = "examples/my-resume.txt"  # 命令行版默认读的简历
DEFAULT_JD_PATH = "examples/my-jd.txt"          # 命令行版默认读的 JD

# ===== LLM 模型配置 =====
# 可选模型列表(网页下拉框用)
MODELS = ["deepseek-v4-flash", "deepseek-v4-pro"]
# 默认用的模型:flash 快/便宜,pro 质量更高(重写简历用 pro)
DEFAULT_MODEL = "deepseek-v4-flash"
# 创意程度 0~1:0=死板确定,1=脑洞大开,简历优化用 0.7 平衡
TEMPERATURE = 0.7
# AI 回复最长 token:之前设 2000 会截断建议,提到 4096;
# 第 12 课加了岗位知识参考(prompt 变长),AI 输出也更啰嗦,再提到 8192
MAX_TOKENS = 8192

# ===== 匹配配置 =====
# main.py(命令行版)演示用的 JD 关键词,第 3 课练过从真实 JD 里提炼
DEFAULT_JD_KEYWORDS = [
    "Python", "CLAUDE", "API", "LLM", "RAG",
    "MYSQL", "Git", "ollama", "deepseek",
    "MCP Server", "RPA", "Agent",
]

# ===== 导出配置(第 9 课)=====
# 重写整份简历用的模型:先试用 flash(便宜),不满意再切 pro(质量更高)
REWRITE_MODEL = "deepseek-v4-flash"
# 重写整份简历输出上限:输出内容比"建议"多得多,单独设大,防截断
# 第 12 课加了岗位知识参考后,AI 要额外融入参考要求,输出更长,再提到 16384
REWRITE_MAX_TOKENS = 16384
# 优化版简历导出到哪个文件
OUTPUT_PATH = "output/optimized_resume.txt"
