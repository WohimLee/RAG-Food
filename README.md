# RAG-Food

## 项目结构

```
rag_food_project/
│
├── app/                     # 🔧 主系统逻辑模块
│   ├── __init__.py
│   ├── api/                 # 📡 接口服务层（FastAPI）
│   │   ├── __init__.py
│   │   ├── endpoints.py     # 用户问题入口、上传数据接口
│   │   └── schema.py        # 请求/响应 Pydantic 模型
│   │
│   ├── core/                # 🧠 模型与管道核心模块
│   │   ├── rag_pipeline.py  # 整个RAG流程组合（检索→生成）
│   │   ├── retriever.py     # 向量召回逻辑（Milvus/BM25）
│   │   ├── generator.py     # 生成模块（LLM调用）
│   │   ├── intent.py        # 意图识别模型（分类器）
│   │   ├── ner.py           # 实体识别模型（NER抽取）
│   │   └── prompt_template.py # 不同意图/风格的prompt模板
│   │
│   ├── db/                  # 🗃 数据库操作
│   │   ├── mysql_client.py  # 菜谱结构查询
│   │   ├── neo4j_client.py  # 食材图谱关系查询
│   │   ├── milvus_client.py # 向量库CRUD
│   │   └── redis_client.py  # 用户session缓存/向量缓存
│   │
│   ├── data_loader/         # 📥 数据导入和更新
│   │   ├── __init__.py
│   │   ├── load_recipes.py  # 读取JSON/CSV菜谱并导入MySQL
│   │   ├── update_vectors.py# 增量生成embedding写入Milvus
│   │   ├── build_kg.py      # 构建Neo4j图谱数据
│   │   └── embedding.py     # 通用embedding生成函数
│   │
│   └── utils/               # 🛠 工具函数
│       ├── logger.py        # 日志模块
│       ├── timer.py         # 用于统计模块耗时
│       └── config.py        # 全局配置（数据库地址、模型路径等）
│
├── tests/                   # 🧪 单元/集成测试
│   ├── test_retriever.py    # 检索质量测试（recall@k等）
│   ├── test_generator.py    # 生成效果测试（BLEU等）
│   ├── test_pipeline.py     # 整体RAG流程测试
│   ├── test_ner_intent.py   # 意图识别与NER测试
│   └── mock_data.json       # 测试用问题/菜谱数据
│
├── scripts/                 # ⚙️ 管理与调度脚本
│   ├── run_server.py        # 启动FastAPI服务
│   ├── daily_update.py      # 定时增量更新脚本（向量+MySQL）
│   ├── rebuild_index.py     # 全量重建Milvus索引
│   └── eval_rag.py          # 用Ragas评估RAG整体性能
│
├── notebooks/               # 📓 实验/数据分析（Jupyter）
│   ├── explore_user_intents.ipynb
│   ├── visualize_kg.ipynb
│   └── prototype_demo.ipynb
│
├── data/                    # 🗂 初始样本数据
│   ├── raw/                 # 原始数据（json/csv）
│   ├── processed/           # 清洗后的数据文件
│   └── embeddings/          # 生成的向量（可缓存）
│
├── .env                     # 环境变量（API密钥、数据库连接）
├── requirements.txt         # 依赖库清单
├── README.md                # 项目说明文档
└── pyproject.toml           # Python项目构建配置（可选）

```

## 各模块作用说明
### 🔧 app/
系统主逻辑模块：
- api/：通过 FastAPI 提供 REST 接口，支持问答调用、上传数据、状态查询。
- core/：
    - rag_pipeline.py：将意图识别 + 检索 + 生成整合为统一接口
    - retriever.py：基于Milvus/FAISS等的Top-k召回
    - generator.py：封装LLM调用（Qwen、OpenAI等），带Prompt构建
    - intent.py / ner.py：意图识别与实体识别模块，封装模型加载与预测

- db/：
    - mysql_client.py：用于结构化字段筛选、推荐、分页查询等
    - neo4j_client.py：食材-属性图谱的多跳关系查询
    - milvus_client.py：embedding生成与Milvus连接（插入/更新/检索）
    - redis_client.py：缓存用户问题、embedding查询结果、会话历史

- data_loader/：
    - 提供菜谱导入、图谱构建、向量生成等可复用任务。

- utils/：通用工具，如日志、耗时统计、全局配置。

### 🧪 tests/
测试模块：

- 单元测试每个子系统是否正常工作（检索、生成、NER、意图）
- 提供Mock样本，用于集成测试整条问答流程
- 可集成到CI（如GitHub Actions）中

### ⚙️ scripts/
调度与运维脚本：

- run_server.py：运行FastAPI服务
- daily_update.py：定时拉取新增菜谱 + 更新Embedding
- rebuild_index.py：全部重建（适用于结构变动后）
- eval_rag.py：使用Ragas/自定义评估工具对系统性能打分

### 📓 notebooks/
快速原型、数据分析、可视化模块：

- 用户意图探索（词云、聚类）
- 菜谱图谱可视化
- 多模型对比测试

### 🗂 data/
数据目录：

- raw/：你最初上传的样本文件，如samples.json
- processed/：转换成结构化字段的数据
- embeddings/：向量文件（可缓存于磁盘/Redis）

### 🏁 项目运行建议
>启动服务
```
python scripts/run_server.py
```

>本地测试
```
pytest tests/
```

>每日数据增量更新
```
python scripts/daily_update.py
```

>RAG系统效果评估
```
python scripts/eval_rag.py
```