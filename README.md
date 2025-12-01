# cal_red_by_openalex
Calculate References Estrangement Degree (RED) of academic papers via OpenAlex API. Upload CSV with DOIs to get metrics (refs/links/density/RED) and download structured results. （借助OpenAlex API计算学术论文参考文献疏离度，上传DOI的CSV文件即可获取指标并下载结果）


# 学术论文参考文献疏离度计算工具
A tool to calculate the References Estrangement Degree (RED) of academic papers via OpenAlex API, based on known DOIs.

## 核心功能
借助 OpenAlex API 接口，实现学术论文参考文献网络的自动化分析：
- 上传含 `doi` 列的 CSV 文件（每行一个论文DOI号）
- 批量获取目标论文的参考文献列表及网络关系
- 计算核心指标：节点数（refs）、连边数（links）、网络密度（density）、参考文献疏离度（RED）
- 生成结构化结果 CSV 并支持下载，含 `doi、refs、links、density、RED` 五列数据

## 主要特性
✅ 批量处理：支持多DOI同时分析，自动过滤空值和无效格式  
✅ 实时反馈：计算过程中实时显示处理进度和参考文献数量  
✅ 错误兼容：单个DOI处理失败不影响整体流程，结果标记"获取失败"  
✅ 易用界面：基于 Streamlit 开发，无需编程基础即可操作  
✅ 灵活部署：本地运行/云端部署（Streamlit Cloud）均可，支持公开访问  

## 使用方法
1. 准备 CSV 文件：确保文件包含名为 `doi` 的列，每行填入有效论文DOI
2. 运行工具：`python -m streamlit run doi_red_calculator.py`
3. 上传文件 → 点击"开始计算" → 下载结果 CSV

## 技术依赖
- Python 3.8+
- 核心库：`streamlit`（网页界面）、`pyalex`（OpenAlex API交互）、`pandas`（数据处理）、`requests`（网络请求）

## 部署说明
可直接部署至 Streamlit Cloud：
1. 将代码推送到 GitHub 仓库
2. 在 Streamlit Cloud 关联仓库，选择主文件 `doi_red_calculator.py`
3. 部署完成后生成公开访问链接，支持多人协作使用

## 指标说明
- **refs（节点数）**：目标论文的参考文献总数  
- **links（连边数）**：参考文献之间的相互引用关系数量  
- **density（网络密度）**：参考文献网络的紧密程度（公式：`2L/(N(N-1))`）  
- **RED（参考文献疏离度）**：衡量参考文献网络的分散程度（公式：`1 - D^(1/3)`）
