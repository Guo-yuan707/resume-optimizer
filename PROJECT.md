# PROJECT.md —— 项目总控制台

> **新对话开始前,先读这个文件。** 这里记录了这个项目"是什么、做到哪了、接下来干嘛"。
> 配套:NOTES.md(学习笔记)、INTERVIEW.md(面试问答)。

## 一、项目是什么

**简历优化助手**:输入简历 + 目标职位描述(JD),分析关键词匹配度、检查简历质量问题,并用大模型生成优化建议,最终导出优化版简历。

开发者:郭园,准大四,准备 2026 秋招。**Python 基础薄弱**,学这个项目的同时补 Python。对 Python 有基础且有兴趣。

## 二、已确定的技术决策(用户拍板的)

| 项 | 决定 |
|----|------|
| AI 接入 | **DeepSeek**(已定,OpenAI 兼容)。openai 库 + base_url=`https://api.deepseek.com`(或 `/v1`,两种都行)。**模型名用新名**:`deepseek-v4-flash`(默认,快/便宜)或 `deepseek-v4-pro`(质量更高,重写简历用这个)。⚠️ 旧名 `deepseek-chat`/`deepseek-reasoner` 已 2026-07-24 弃用,别用。API key 存 `.env`,第5课配置。 |
| 界面 | Streamlit 网页 |
| 简历输入格式 | 主要 PDF,开发期先用 txt 方便调试(也要支持 docx/md) |
| 求职市场 | 中英双语都要 |
| 推进方式 | **边写边讲 + 练习**,每课配 NOTES.md + INTERVIEW.md |

## 三、怎么运行

```bash
cd "d:/Project/resume optimize"
.venv/Scripts/activate                    # 进入虚拟环境(前缀出现 (.venv) 即成功)
.venv/Scripts/python main.py              # 命令行入口:跑完整链路(解析→匹配→检查→RAG→AI 建议→导出)
.venv/Scripts/python -m streamlit run app.py   # 网页入口:浏览器打开 http://localhost:8501
```

- 环境:Python 3.14.6,虚拟环境在 `.venv/`
- 编码:Windows 控制台乱码问题已解决(入口调用 `sys.stdout.reconfigure(encoding="utf-8")`)

## 四、文件结构(每个文件干嘛)

```
项目根目录/
├── main.py            # 入口,运行它跑整个程序(命令行版,用户主要看这个)
├── app.py             # 网页入口(第6课):`streamlit run app.py` 启动浏览器版
├── config.py          # 集中配置(第7课):所有可调参数(模型/温度/路径/关键词)
├── README.md          # 项目门面(第7课):说明 + 快速开始 + 结构 + 技术栈
├── requirements.txt   # 依赖清单(第7课):pip install -r requirements.txt
├── resume_optimizer/  # 代码包
│   ├── __init__.py    # 空文件,标记这是包
│   ├── parser.py      # 解析模块:read_text() + Resume 数据类 + parse_resume()
│   ├── matcher.py     # 匹配模块(第3课):match_keywords() 关键词比对
│   ├── checker.py     # 质量检查(第4课):check_all() 统一跑检查规则
│   ├── llm.py          # LLM 调用(第5课):封装 DeepSeek API,拼 prompt,返回优化建议
│   ├── exporter.py     # 导出(第9课):save_resume() 把改写后的简历写进文件
│   ├── knowledge.py    # 知识库(第10课):read_knowledge_files() 读岗位文档 + chunk_text() 切块
│   │                   #   + build_knowledge_context() 检索知识库拼参考段落(第12课)
│   ├── retriever.py    # 向量检索(第11课):build_knowledge_index() 建索引 + retrieve() 检索
│   └── loader.py       # 文件读取(第15课):extract_text() 把上传的 txt/pdf/docx/jpg/png 全抽成纯文本
├── tests/             # 单元测试(第7课起):pytest,62 个用例全绿
│   ├── test_parser.py # 测解析模块
│   ├── test_matcher.py# 测匹配模块
│   ├── test_checker.py# 测检查模块
│   ├── test_llm.py    # 测 JD 关键词解析 + prompt 注入(纯函数,不联网)
│   ├── test_exporter.py# 测文件写入(第9课)
│   ├── test_knowledge.py # 测知识库切块/检索(第10/13课)
│   ├── test_retriever.py # 测向量化+相似度(第11课,纯数学)
│   └── test_loader.py  # 测多格式读取(第15课):txt 编码回退/docx/pdf/报错
├── examples/          # 测试数据(进公开仓库的是假数据)
│   ├── resume.txt     # 示例假简历(第1课,公开)
│   ├── sample-jd.txt  # 示例 JD(第3课,公开)
│   └── knowledge/     # 岗位知识库(第10课):真实岗位要求文档(公开)
├── output/            # 导出文件(第9课):程序生成,已 .gitignore,不进 git
│   └── optimized_resume.txt   # AI 改写后的简历存这里
├── PROJECT.md         # 项目总控制台:是什么、做到哪、接下来干嘛
├── NOTES.md           # 学习笔记(每课知识点 + 踩坑记录)
├── INTERVIEW.md       # 面试问答集(这个项目的专属八股)
├── CAREER.md          # 求职备战总清单(四块能力 + 资源 + 进度勾选)
├── .env               # API Key 配置文件(第5课:不进入版本控制)
├── .env.example       # API Key 模板(第7课:提交到 git,别人照着建 .env)
├── .gitignore         # 保护:.env / .venv / output + 真实个人简历与 JD(含手机号,不进公开仓库)
├── .streamlit/        # (第15课)Streamlit 主题配置 config.toml:页面基础配色
└── .venv/             # Python 虚拟环境,自动生成,永不手动改
```

## 五、学习路线 + 进度

| 阶段 | 内容 | 要学的 Python | 状态 |
|------|------|--------------|------|
| 第1课 | 环境搭建 + 读文本简历 | venv/pip、函数、with open、if __name__、编码 | ✅ 完成 2026-08-02 |
| 第2课 | 解析简历为结构化数据 | 列表、字典、dataclass、类 | ✅ 完成 2026-08-02 |
| 第3课 | 关键词匹配职位 JD | 字符串、正则表达式 | ✅ 完成 2026-08-03 |
| 第4课 | 质量检查器 | try/except 异常处理 | ✅ 完成 2026-08-03 |
| 第5课 | 接入 LLM,AI 重写 | HTTP 请求、API、JSON | ✅ 完成 2026-08-04 |
| 第6课 | Streamlit 网页界面 | Web 应用概念 | ✅ 完成 2026-08-04 |
| 第7课 | 工程化收尾 + 文档 | 配置、日志、测试 | ✅ 完成 2026-08-04 |
| 第8课 | AI 自动提取 JD 关键词 | JSON 解析、正则、结构化输出 | ✅ 完成 2026-08-04 |
| 第9课 | 导出优化版简历 | 文件写入、抽公共函数、输出格式兼容 | ✅ 完成 2026-08-07 |
| 第10课 | RAG:概念+知识库+切块 | 目录读取、列表推导、while、rfind | ✅ 完成 2026-08-08 |
| 第11课 | RAG:本地向量化+相似度检索 | 向量、TF-IDF、余弦相似度 | ✅ 完成 2026-08-11 |
| 第12课 | RAG:检索结果注入 prompt | 可选参数、prompt 注入、token 预算 | ✅ 完成 2026-08-13 |
| 第13课 | RAG 收尾:测试 + 清单核对 | tmp_path、monkeypatch | ✅ 完成 2026-08-13 |
| 第14课 | git + 部署上线 | git 基础、.gitignore 保护、gh、Streamlit Cloud、TOML Secrets | ✅ 完成 2026-08-15 |
| 第15课 | 界面升级(简约专业风)+ 多格式上传 | 多格式解析(pdf/docx)、图片 OCR、懒加载、Streamlit 主题/CSS | ✅ 完成 2026-09-03 |

## 六、已完成记录

### 第1课(2026-08-02)
- 建好 venv、包结构、parser.read_text()、main.py 入口
- 修复 Windows 中文乱码(stdout 强制 UTF-8)
- 练习(用户已做,验证通过):
  1. 建 `examples/my-resume.txt` 放真实简历 ✅
  2. main.py 路径改为自己的简历 ✅
  3. 用 f-string + len() 打印字数,输出「简历共1276字」✅

### 第2课(2026-08-02)
- 新增 `Resume` dataclass(5 字段:header/skills/education/projects/strengths)
- 新增 `parse_resume()` 函数:按标题行分段解析,返回 Resume 对象
- main.py 改为调用 parse_resume(),按 5 段打印
- 知识点:list/dict/dataclass/for/split/strip/startswith/append/continue/**拆字典
- 练习(用户已做,验证通过):
  1. 运行 scratch.py 观察非空行列表 ✅
  2. 交互环境验证 split/strip/startswith/for ✅
  3. 口头回答 dict vs dataclass 区别、items() 返回值 ✅

### 第3课(2026-08-03)
- 新增 `resume_optimizer/matcher.py`:`match_keywords()` 函数 — 纯关键词列表匹配
- main.py 新增 JD 关键词匹配环节:硬编码关键词列表 → 调用 match_keywords → 打印 ✅/❌ + 匹配率
- 新建 `examples/sample-jd.txt`:一份示例 JD,以后可以从中提取关键词
- 知识点:in 运算符、lower() 统一大小写、if/else 条件分支、循环+判断+计数模式、f-string 百分比格式化、dict 返回多值
- 运行验证:简历 vs 12 个关键词,命中 8 个(67%)
- 练习(用户已做,验证通过):
  1. 交互环境观察 in + lower() 行为,解释为什么 .lower() 前后结果不同 ✅
  2. 建 examples/my-jd.txt 放真实 JD,提炼 12 个关键词,匹配率 42% ✅
  3. 口头解释 in vs ==:in 找"里面有没有",== 要"完全相等",匹配场景用 in ✅

### 第4课(2026-08-03)
- 新增 `resume_optimizer/checker.py`:5 条检查规则 + `check_all()` 统一调度
- 规则清单:联系方式检查、4 段长度检查、2 段空项检查、整体长度检查
- main.py 新增质量检查环节:调用 check_all() → 逐条打印结果 → 统计通过/未通过
- 知识点:try/except 异常处理、any() 判断迭代器、enumerate() 带序号遍历、getattr() 动态取属性、sum() + 生成器表达式
- 运行验证:郭园真实简历 8 项全部通过,总长 1212 字
- 练习(已完成 2026-08-03):
  1. 交互环境体验 try/except ✅
  2. 交互环境体验 any vs all ✅
  3. 交互环境体验 enumerate ✅
  4. 给 checker.py 加 check_education_quality ✅
  5. 口头解释 try/except、any/all、getattr ✅

### 第5课(2026-08-04)
- 新建 `resume_optimizer/llm.py`:封装 DeepSeek API 调用,含 `_build_client()`、`build_prompt()`、`get_optimization_advice()` 三个函数
- 新建 `.env`:存 API Key 和 Base URL,不进入版本控制
- 新建 `.gitignore`:忽略 `.venv/`、`.env`、`__pycache__/`
- main.py 新增 AI 优化建议环节:调用 `get_optimization_advice()` → 打印 AI 生成的优化建议,try/except 兜底
- 安装 openai + python-dotenv 两个第三方库
- 知识点:HTTP API 调用、环境变量、Chat Completion API、Prompt 工程、temperature/max_tokens 参数
- 运行验证:DeepSeek API 连接成功,AI 针对缺失关键词(7个)逐条给出融入方案 + STAR 法则改写建议
- 练习(待用户完成):
  1. 查看 DeepSeek 后台的 token 消耗
  2. 对比 deepseek-v4-flash vs deepseek-v4-pro 的建议差异
  3. 修改 prompt 的任务要求,加自己的定制条件

### 第8课(2026-08-04,AI 自动提取 JD 关键词)
- llm.py 新增 `extract_keywords_from_jd()`(调 AI)+ `parse_keyword_json()`(解析,纯函数)
- app.py 侧边栏加 JD 上传/粘贴,点分析后 AI 自动提取关键词 → st.multiselect 多选确认 → 匹配;手动关键词兜底
- 新增 `tests/test_llm.py` 7 个用例(只测解析纯函数,不测 API 调用),总计 30 用例全绿
- 知识点:结构化输出、json.loads、正则 re.search + re.DOTALL、容错解析、温度低值(0.3)用于提取、拆"调AI/解析"两函数复用测试边界
- 运行验证:真实调用 DeepSeek 从示例 JD 提取出 20 个关键词 ✅

### 第7课(2026-08-04,轻量工程化)
- 装 pytest,新建 `tests/` 三个测试文件,23 个用例全绿(parser/matcher/checker)
- 新建 `config.py` 集中配置,llm.py / main.py / app.py 三个文件改用 config
- 新建 `README.md` 项目门面 + `.env.example` 模板 + `requirements.txt` 依赖清单
- 选择"轻量工程化":项目还小,只做测试 + 配置 + README,日志跳过
- 知识点:assert、pytest、测试组织约定、测试边界(不测 llm 因为它要调真实 API 花钱)、魔法数字、config 集中配置、README 结构
- 踩坑记录:测试失败先判断"代码错还是测试错"(两次都是测试自己写错了)
- 运行验证:23 tests passed;config 导入正常;命令行/网页入口不受影响

### 第6课(2026-08-04)
- 安装 Streamlit 1.60.0
- 新建 `app.py` 网页入口:左侧边栏输入(上传简历、填关键词、选模型、按钮) + 主区域输出(匹配/检查/AI 建议)
- 把第 1~5 课的 parser/matcher/checker/llm 四个模块一行不改接到网页上
- 修复 AI 回复截断问题:max_tokens 2000→4096 + finish_reason 检查兜底
- 知识点:Web 应用 vs 命令行、Streamlit 组件(layout/file_uploader/text_input/selectbox/button/progress/spinner/success/error)、脚本重跑机制、文件上传 vs 本地读、finish_reason
- 运行验证:浏览器上传简历/填关键词/选模型 → 完整分析+AI建议 ✅

### 第9课(2026-08-07,导出优化版简历)
- 新增 `resume_optimizer/exporter.py`:`save_resume()` 把改写后的简历写进文件(`open(path, "w")` 写入 + `os.makedirs` 建目录)
- llm.py 新增 `_summarize_analysis`(抽公共函数,DRY)+ `build_rewrite_prompt` + `get_rewritten_resume`(让 AI 直接输出整份改写简历,默认用 pro)
- config.py 新增 `REWRITE_MODEL` + `OUTPUT_PATH`
- main.py 新增"导出优化版简历"环节;app.py 新增 `st.download_button` 下载按钮
- 新增 `tests/test_exporter.py` 3 个用例(文件写入,用 tmp_path,不联网),总计 33 用例全绿
- 知识点:文件写入(open "w" / write / utf-8)、os 路径处理、抽公共函数、AI 输出格式与下游工具兼容、st.download_button
- 实战踩坑:AI 把标题写成 `**专业技能**`(加了 markdown 星号),parse_resume 认不出导致四段全空 → prompt 说死"禁止任何 markdown 标记"后解决
- 运行验证:命令行导出成功,回读五段全部正确 ✅

## 七、9 课主线完成 + RAG 升级中(第 10~13 课)

> ✅ **RAG 知识库升级已全部完成(2026-08-13)**:检索 → 增强 → 生成 全链路落地,54 个测试全绿。项目现可当"带知识库的简历优化助手"去面试讲。

### RAG 升级计划(第 10~13 课)

**做什么**:给工具加一个"岗位知识库",AI 改写简历时从库里检索与当前 JD 最相关的真实岗位要求,拼进 prompt 作参考——让改写贴合行业真实要求,而不是 AI 空想(开卷考试 vs 闭卷考试)。

**技术决定(已定,别改)**:
- 知识库 = 一摞真实岗位要求文档(放 `examples/knowledge/` 下)
- 检索用**本地向量化**(词频权重 + 余弦相似度),**不用 DeepSeek embedding API**——官方向量接口不确定(2026-08 查证),且亲手实现能讲清原理,正好补上 Egg 项目里"讲不明白"的 RAG/向量化部分
- 流程:上传当前 JD → 从知识库检索最相关几段 → 拼进 `build_prompt` / `build_rewrite_prompt` → AI 参考改写

| 课 | 内容 |
|---|---|
| 第 10 课 | RAG 概念 + 建知识库数据 + 切块函数 | ✅ 完成 2026-08-08 |
| 第 11 课 | 本地向量化 + 相似度检索 | ✅ 完成 2026-08-11 |
| 第 12 课 | 接进现有改写流程(prompt 注入) | ✅ 完成 2026-08-13 |
| 第 13 课 | 测试、文档、INTERVIEW/CAREER 收尾 | ✅ 完成 2026-08-13 |

### 第 10 课(2026-08-08,RAG 概念 + 知识库 + 切块)

- 新增 `examples/knowledge/` 岗位知识库:3 份示例岗位文档(ai-application-engineer / rag-engineer / python-backend-dev),贴合用户投递方向
- 新增 `resume_optimizer/knowledge.py`:`read_knowledge_files()` 扫描目录读所有 .txt + `chunk_text()` 按空行分段、长行按标点切块
- 知识点:RAG 概念(检索+增强+生成)、os.listdir/isdir/join/abspath、列表推导式、str.rfind 从右找标点、while 循环切块、内部函数 `_` 前缀
- 运行验证:3 份文档(638/575/490 字)分别切成 20/19/19 块,每块语义完整 ✅
- 技术决定落实:检索用本地实现(第 11 课),不用 DeepSeek embedding API

### 第 11 课(2026-08-11,RAG 本地向量化 + 相似度检索)

- 新增 `resume_optimizer/retriever.py`:`cosine_similarity` / `build_knowledge_index` / `retrieve`
- 新增 `tests/test_retriever.py`(9 个,纯数学函数)+ `tests/test_knowledge.py`(7 个,补第 10 课漏的)
- 知识点:向量、TF-IDF、余弦相似度、点积、zip、lambda、pytest.approx、浮点精度坑
- 运行验证:3 份知识库文档(58 块)建索引,JD 检索出最相关块 ✅

### 第 12 课(2026-08-13,RAG 检索结果注入 prompt)

- `llm.py`:`build_prompt` / `build_rewrite_prompt` / `get_optimization_advice` / `get_rewritten_resume` 加 `knowledge_context` 参数(默认空串,prompt 有值时拼【岗位知识参考】)
- `knowledge.py`:新增 `build_knowledge_context(jd_text, top_k=3)` 一条龙:读→切→索引→检索→拼编号段落
- `main.py` + `app.py`:入口接上——读 JD 检索,把参考传给两个 AI 调用;网页版加"📚 AI 参考的岗位知识"折叠框
- 踩坑:加了参考后 AI 输出变长,4096/8192 都被截断(改写简历断在"工具"二字、警告混进导出文件)→ `config.py` 里 `MAX_TOKENS`→8192、`REWRITE_MAX_TOKENS`→16384
- 运行验证(真实调 API):检索到 3 块最相关岗位要求;AI 建议正常;导出简历完整、融入参考要求(OpenAI 兼容接口/DeepSeek、RAG、MCP Server),缺失关键词补齐 ✅

### 第 13 课(2026-08-13,RAG 收尾:测试 + 清单核对)

- 新增测试 5 个(49→54 全绿):
  - `tests/test_llm.py` +3:build_rewrite_prompt 传参考/不传/传空串 → prompt 是否含【岗位知识参考】
  - `tests/test_knowledge.py` +2:build_knowledge_context 用 `tmp_path` + `monkeypatch` 造临时知识库测检索命中/空库返回空串
- 踩坑(测试预期太具体):断言"搜到岗位名称块"失败——JD 含 FastAPI 时,"要求"块相似度更高被选中。检索没错,是断言写死错了;改为断言"搜到 Python 相关、且无无关前端"
- 知识点:`tmp_path`(pytest 每个测试发一个专属临时目录)、`monkeypatch`(测试时临时改路径/变量,测完自动还原)
- CAREER.md 进度勾选更新:第 5/6 课、RAG 重做完成;NOTES/INTERVIEW 已含第 12/13 课内容

9 课主线已全部完成:命令行版 + 网页版 + 测试 + 配置 + README + 导出。项目已经是一个"拿得出手"的完整作品。以后想升级,可选方向(按 PROJECT.md 早期定下的计划):

1. **支持 PDF/docx/md**:现在只收 .txt,正式求职简历大多是 PDF;JD 目前也只收文本
2. **JD 图片 OCR**:DeepSeek 不收图片,JD 截图要先 OCR(装 RapidOCR)再走文本链路
3. **中英双语支持**:求职市场中英双语都要(项目初期决策)
4. **日志 logging**:本次轻量工程化跳过了,以后项目复杂了补上

> 导出优化版简历(原第 1 条)已在第 9 课完成 ✅
> 原「可选方向」第 1 条(支持 PDF/docx/md 上传)、第 2 条(JD 图片 OCR)已在第 15 课完成 ✅(2026-09-03)

升级时记得:**先跑一遍测试确保全绿,再动手改**——安全网就是这样用的。

## 八、给新对话的我的提示

- 用户 Python 基础薄弱,用生活化的例子
- **重要背景**:用户简历(my-resume.txt)里列的项目(如 Egg AI 聊天应用)是当初靠 AI 一口气生成的,用户自己看不懂、无法向面试官解释,因此那份简历"泡汤了"。**本项目的一个重要价值:让用户亲手做出一个自己能讲明白的 Python 项目**(就是本工具自己),未来可作为简历主打项目。讲解任何代码都要确保用户真的懂,不要只求功能跑通。
- 用户明确要求:**每建一个新文件,先解释它是干嘛的再建**,一次一课,不要批量建文件
- 每课必须更新 NOTES.md 和 INTERVIEW.md(这是用户的面试资料)
- 进度更新:每完成一课就更新本文件的"五、进度表"
- 当前 Python 3.14.6,装库用 `.venv/Scripts/pip install xxx`,运行用 `.venv/Scripts/python`
- **现在有两个入口**:`python main.py`(命令行,第1-5课)和 `streamlit run app.py`(网页,第6课),两个入口共享同一套模块
- **第 15 课起网页版 UI 已改版**(详见第十节):去侧边栏 → 居中单栏卡片风;去掉手动关键词(关键词只来自 JD,AI 提取后可删减);简历收 .txt/.pdf/.docx,JD 收文本文件/粘贴/图片(.jpg/.png 自动 OCR)

## 九、项目 1 结课总结(2026-09-02 里程碑)

**一句话意义**:不是"做了个工具",而是让一个 Python 基础薄弱的人,把「从读文本到部署上线」的 AI 应用全链路**每层亲手实现、每层能开口讲**,做成简历上真正站得住的主打项目(替代当初讲不明的 Egg 项目)。

**一张表看懂 14 课的成长链**:

| 阶段 | 做了啥 | 亲手实现 vs 借力 | 面试能讲 |
|---|---|---|---|
| 解析(第1-2课) | 读简历 → Resume 结构化 | 亲手:标题行分段、dataclass | 把非结构化文本变结构化 |
| 匹配(第3课) | 简历 vs JD 关键词比对 | 亲手:大小写归一、算匹配率 | `in` vs `==`、命中率怎么算 |
| 检查(第4课) | 9 条质量规则 | 亲手:try/except 兜底 | 检查怎么做到不崩 |
| LLM(第5课) | 调 DeepSeek 出建议 | 借力:openai SDK(OpenAI 兼容) | prompt 工程、token、temperature |
| Web(第6课) | Streamlit 网页版 | 借力:框架 | 网页 = 把模块接到 UI |
| 工程化(第7课) | config / README / pytest | 亲手:测试边界设计 | 为何只测纯函数、不测真实 API |
| 结构化输出(第8课) | AI 提取 JD 关键词 | 亲手:正则 + json.loads 容错 | AI 输出怎么保健壮 |
| 导出(第9课) | AI 整份改写 → 存文件 → 可回读 | 亲手:文件写入、抽公共函数 | 输出与下游兼容的坑(禁 markdown) |
| RAG(第10-12课) | 切块 → TF-IDF → 余弦检索 → 注入 prompt | 亲手:整套检索,**不调 embedding API** | 向量 ≠ 关键词、开卷 vs 闭卷、token 预算 |
| 收尾(第13课) | tmp_path / monkeypatch | 亲手 | 测试不碰真实文件 |
| git+部署(第14课) | GitHub + Streamlit Cloud | 亲手:gh 命令行 | TOML Secrets 的坑 |

**硬成果**:线上可点(网页 resume-optimizer-yeazwx2nnetzxfxgmuthmn.streamlit.app / GitHub github.com/Guo-yuan707/resume-optimizer);62 个 pytest 全绿;命令行 + 网页双入口;用自己的工具反哺自己——真实简历与目标 JD 的关键词匹配率 42% → 50%(同套词、工具实测),简历 v2 打磨到可投、工具自查 9/9。

**「能讲」与「还不能上简历」边界**:
- 能讲清(可写简历、可深挖):RAG 全链路 / 结构化输出容错 / 测试边界 / token 与输出预算 / 云端部署链路
- 还不能(别写,一问就穿帮):**Agent、Function Calling、MCP Server** ← 这是项目 2 的动机
- 反例教训:当初 Egg 项目靠 AI 一口气生成、自己讲不明 → 弃用。**简历上每个词都得能现场演示**

**遗留待办(2026-09-02 记录,避免丢失)**:
1. 公开仓库新克隆跑 `python main.py` 会因默认简历路径是私有文件而报错 —— 已识别的坑,暂不修(个人主要走网页版)
2. INTERVIEW.md「深挖题4 部署」还标着"待练",下次磨成金句
3. 第一个稳妥投递靶待定(my-jd.txt 那份 JD 要求偏硬:本地模型/DB/Agent/MCP)
4. 项目 2 方向待拍板(主线是补 Agent / Function Calling)

## 十、第 15 课已完成记录(2026-09-03):界面升级 + 多格式上传

**一句话**:把网页端从"学生作品感"升级成"简约专业风",并让上传贴近真实求职场景 —— 简历支持 .txt/.pdf/.docx,JD 支持文本文件 / 图片(.jpg/.png 自动 OCR)/ 粘贴。

### 需求 + 用户拍板的决策
- UI:清爽浅色专业风(浅灰底 + 白底圆角卡片 + 单一靛蓝强调色)、**居中单栏**(去掉侧边栏);模型等参数收进折叠的「高级选项」
- 输入:简历和 JD 是**两个独立上传窗**(不是合成一个拖拽框);**去掉手动关键词** —— 关键词只来自 JD(AI 提取后可勾选删减)
- Word 只支持 `.docx`(老 .doc 在云端 Linux 难解,已确认);PDF 只支持**文字型**(扫描版不 OCR,如实友好提示)
- JD 三种来源:上传 .txt/.md、上传 .jpg/.png(OCR)、粘贴文本;**未传 JD → 醒目提醒 + 降级只跑质量检查**

### 做了什么
| 文件 | 改动 |
|---|---|
| `resume_optimizer/loader.py` | **新增**:extract_text() 按扩展名把上传的内存字节抽成纯文本;txt 编码 utf-8 → gb18030 兜底;pdf 用 pypdf、docx 用 python-docx(段落+表格)、图片用 RapidOCR;重库全部懒加载、OCR 引擎单例缓存、双 import 兼容 |
| `app.py` | **重写**:居中单栏 + 一张输入卡(简历/JD 两个独立上传窗)+ 结果卡片化;无 JD 降级只出质量检查 |
| `config.py` | 新增 `RESUME_ACCEPT` / `JD_ACCEPT` 两个格式清单(前后端共用) |
| `.streamlit/config.toml` | **新增**:页面基础配色(浅色主题、靛蓝 primaryColor) |
| `requirements.txt` | 新增:pypdf、python-docx、rapidocr-onnxruntime(已 pin 版本;cp314 轮子,py3.14 与云端都兼容) |
| `tests/test_loader.py` | **新增** 8 个用例(txt 两种编码 / docx 段落+表格 / PDF / 报错),旧 54 → **62 全绿** |
| `examples/sample-jd.png` | **新增**:示例 JD 截图(OCR 演示 / 测试用,假数据可进公开仓库) |

### 知识点(详见 NOTES.md 第 15 课)
1. 加一层「文件 → 纯文本」适配层(loader):格式扩展只动这一层,parser/matcher/checker/llm/knowledge 一行不改(它们只认文本)
2. 编码兜底:Windows 中文 txt 常见 GBK,utf-8 解不了自动退 gb18030
3. PDF/docx/OCR 库**懒加载**(函数内 import):用到才加载,OCR 缺库也不拖垮整体
4. OCR 本地化:RapidOCR(自带中英文模型,不联网不花钱、隐私好)+ 引擎单例缓存(首次加载慢正常)
5. UI 双管齐下:`.streamlit/config.toml` 管基础配色 + app.py 注入 CSS 管卡片/圆角/字体/留白;居中单栏 = `layout="centered"`
6. 无 JD 降级设计:与其报错卡住,不如先给出能给的(质量检查)+ 醒目提醒引导补 JD

### 踩坑记录(面试可讲)
- `__import__("resume_optimizer.loader")` 实际返回的是**顶层包** `resume_optimizer`,getattr 拿不到子模块里的 `_read_txt` → 改成"分发表的值直接放函数对象",更直白
- pypdf 只"读"不"写"文字型 PDF → 单测夹具是**手写的最小合法 ASCII PDF**;中文 PDF 留真实文件手测
- OCR 首次调用加载模型要几秒;Windows 终端中文乱码只影响显示不影响逻辑(断言用子串比较即可)

### 验证
- **62 个 pytest 全绿**;loader 手验(txt 两种编码 / docx 段落+表格 / PDF 抽取 / 未知扩展名 / 空 PDF)
- Streamlit AppTest 两条**离线**路径通过:只传简历(无 JD)→ 出提醒 + 质量检查卡;不传简历点分析 → 友好报错(不崩)
- OCR 冒烟:示例 JD 截图(中英文)识别 8 行,Python / RAG / Git / 数据分析 / 检索 等全部命中
- ⏳ 待做:浏览器完整走查(含图片 JD 全链路)、`git push` 云端重建验证(需用户点头)
