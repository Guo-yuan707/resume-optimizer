# 📄 简历优化助手

一个用 Python 写的简历优化工具:上传简历 + 填写 JD 关键词,自动分析关键词匹配度、检查简历质量问题,调用 DeepSeek 大模型生成改写建议,还能直接导出改写好的整份简历。

命令行版和网页版都有 —— 网页版用 **Streamlit** 构建,上传文件、填关键词、点按钮即可得到完整分析。

🔗 **在线体验**:https://resume-optimizer-yeazwx2nnetzxfxgmuthmn.streamlit.app/(Streamlit Community Cloud 部署)

## ✨ 功能

- 🔍 **关键词匹配**:把 JD 里的关键词和简历做比对,计算匹配率,标出命中/缺失
- 🩺 **简历质量检查**:9 条规则自动检查(联系方式是否完整、各段落是否充实、有没有空项等)
- 🤖 **AI 优化建议**:基于前面的分析结果,DeepSeek 逐条给出针对性的改写建议(STAR 法则等)
- ⬇️ **导出优化版简历**:让 AI 直接输出一整份改写好的简历,命令行存成文件,网页版一键下载
- 🌐 **网页界面**:Streamlit 网页版,不用碰命令行,浏览器里即可操作

## 🚀 快速开始

**环境要求**:Python 3.14+ ,需要你的 DeepSeek API Key

```bash
# 1. 建虚拟环境并安装依赖
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt

# 2. 配置 API Key(把 key 填进去)
#    复制 .env.example 为 .env,填入你的 DEEPSEEK_API_KEY
#    没有 Key 可以去 https://platform.deepseek.com/api_keys 创建

# 3. 运行 —— 两种方式二选一
.venv/Scripts/python main.py          # 命令行版:终端里看结果
.venv/Scripts/python -m streamlit run app.py   # 网页版:浏览器打开 localhost:8501
```

## 🧪 跑测试

```bash
.venv/Scripts/python -m pytest tests
```

54 个测试覆盖解析(parser)、匹配(matcher)、检查(checker)、JD 关键词解析(llm)、文件导出(exporter)、RAG 知识库(knowledge)与检索(retriever)。

## 📁 项目结构

```
.
├── app.py                    # 网页入口:streamlit run app.py
├── main.py                   # 命令行入口:python main.py
├── config.py                 # 集中配置:所有可调参数(模型、温度、路径等)
├── resume_optimizer/         # 核心代码包
│   ├── parser.py             # 解析:读文本 → 结构化 Resume
│   ├── matcher.py            # 匹配:JD 关键词 vs 简历,算匹配率
│   ├── checker.py            # 检查:9 条质量规则
│   ├── llm.py                # LLM 调用:拼 prompt → DeepSeek → 建议/改写
│   ├── exporter.py           # 导出:把改写后的简历写进文件
│   ├── knowledge.py          # RAG 知识库:读岗位文档 + 切块 + 检索拼参考
│   └── retriever.py          # RAG 检索:TF-IDF 向量化 + 余弦相似度
├── examples/knowledge/       # 岗位知识库(真实岗位要求文档)
├── examples/                 # 测试数据(示例简历 / JD)
├── output/                   # 导出文件存放处(自动生成)
├── tests/                    # pytest 单元测试
├── .env                      # API Key(不提交到 git)
└── .env.example              # API Key 模板
```

## 🛠️ 技术栈

- **Python 3.14** · Streamlit(网页)· openai SDK(调 DeepSeek,OpenAI 兼容接口)· scikit-learn + numpy(RAG 向量化与相似度检索)· python-dotenv(读 .env)· pytest(测试)

## ⚙️ 配置说明

| 配置 | 位置 | 说明 |
|------|------|------|
| API Key | `.env` 的 `DEEPSEEK_API_KEY` | 调 DeepSeek 必须,别提交到 git |
| 模型 / 温度 / max_tokens | `config.py` | 想调 AI 行为改这里,全局生效 |
| 默认简历路径 / JD 关键词 | `config.py` | 命令行版用的默认值 |
