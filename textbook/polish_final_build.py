"""Synchronize final edition metadata and reader documentation."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def edit(name,pairs):
    p=ROOT/name;t=p.read_text(encoding='utf-8')
    for a,b in pairs:t=t.replace(a,b)
    p.write_text(t,encoding='utf-8')
edit('build_book.mjs',[
 ('学术排版修订版','修订版'),
 ('44 章 · 65 组图示 · 8 个项目','44 章 · \'+figureCount+\' 组图示 · 8 个项目')])
edit('finish_layout.py',[("'subject':'学术排版修订版；44 章、65 组图示、8 个项目'","'subject':f\"修订版；44 章、{load('layout_check.json')['figures']} 组图示、8 个项目与真实模型综合案例\"")])
edit('prepare_style_fonts.py',[("cover='深度学习", "cover='最终简明深度学习")])
edit('新版章节/38.md',[('到程序完成验收前测量','到程序完成验收测量')])
edit('figures/gen_final_case_figures.py',[('L14 · 最高均值','L14 · B 类均值')])
edit('排版与编辑说明.md',[
 ('# 学术排版修订说明','# 修订版排版与编辑说明'),
 ('Great Vibes 38 pt','Great Vibes 28 pt'),('署名为 Violet。','署名依次为 Violet、Star、Sapphire。'),
 ('目录展开到全部节，包含点状引导线、右对齐页码和内部跳转。','简明总目录展示三篇与 44 章主线，详细目录展开到全部节，包含点状引导线、右对齐页码和内部跳转。')])
edit('数据与引用说明.md',[
 ('真实模型任务评估按第 38 章另行设计。','新增 DeepSeek 真实模型实验单独保存在 case_study/lungsight，方法与结果见第 38.10—38.11 节。'),
 ('也不计入正文的 65 组图示。','也不计入正文图示总数。'),
 ('API 适配器固定 2023-06-01 请求版本','Anthropic 适配器固定 2023-06-01 请求版本')])
edit('agent_projects/README.md',[
 ('固定模型回复是可复现的测试输入；它们不证明模型会自行选择这些工具。','固定模型回复是可复现的测试输入，检查工具与运行时路径；真实模型选择工具的实验见下方 DeepSeek 综合案例。'),
 ('本版没有执行真实模型调用，适配器尚未经过远端集成验证。','本节 Anthropic 适配器完成了本地消息测试；远端实测使用另一份 DeepSeek 适配器。'),
 ('之后另建独立的自然语言任务集评价真实模型，并报告失败案例与成本。','之后另建任务集评价真实模型，并报告失败案例与成本。')])
for filename,heading,content in [
('agent_projects/README.md','## 单独运行与真实模型综合案例',r'''
## 单独运行与真实模型综合案例

默认 `--project all` 运行三个项目；也可以只运行一个，其余项目的结果保持原样：

```powershell
python agent_projects/run_projects.py --project knowledge
python agent_projects/run_projects.py --project analysis
python agent_projects/run_projects.py --project workflow
python agent_projects/sensor_bridge.py
```

知识库输出 `knowledge_trace.json`；订单输出 `analysis_trace.json` 与 `orders_report.md`；工单输出 `workflow_trace.json`，共同摘要为 `offline_results.json`。桥接输出为 `sensor_bridge.json`，连接已保存的模拟 CNN 预测、虚构手册与待批准提案，使用离线模型回放。

真实模型综合案例位于 `case_study/lungsight`，使用 `deepseek_provider.py` 和三种只读工具。保存了 20 道冻结教学题、重复运行、超时对照以及来源表达修订前后的报告，使用 DeepSeek 官方接口实际执行。运行方法、具体检查范围与费用参考见该目录的 README 和教材第 38.10—38.11、40.10—40.14 节。
'''),
('数据与引用说明.md','## 修订版：公开项目与真实模型实验',r'''
## 修订版：公开项目与真实模型实验

LungSight 案例引用 [wxy11117/LungSight 的固定提交](https://github.com/wxy11117/LungSight/tree/80932e2d34eefbfd3031e0a04370986562cf40ac)。随包保存 README、Agent 服务、RAG 评测脚本和模式说明的来源快照；8 段资料在 documents.json 中记录文件、行号、链接与版本，source_manifest.json 保存文件哈希。

教学任务 DEMO-001、DEMO-002 的四类概率是作者构造数据，并非患者推理输出。任务仅借用项目接口中的架构、权重标识和状态字段组织方式。20 道题是作者围绕同一证据包编写的冻结教学任务；2 道开发题与它们共享资料。实验检验实际模型调用、只读工具、指定事实与来源条件，不涉及临床评价或上游系统状态变更。

DeepSeek 接口请求和返回均记录 deepseek-flash，调用日期为 2026-11-10。使用非思考模式，见 [官方工具调用说明](https://api-docs.deepseek.com/guides/tool_calls/)。费用按当日 [官方价格表](https://api-docs.deepseek.com/quick_start/pricing/) 的高峰缓存未命中输入价和高峰输出价估算；usage 来自实际响应，估算单列，不充当账户扣款凭据。完整响应正文与检查结果保存在 case_study/lungsight/results，密钥及本机私有配置排除在资料包外。

综合报告的数值检查与编辑语义审查分开记录。REPORT01 的来源表述问题和 REPORT02 的修订输出均保留；semantic_review.json 记录文字与来源复核，属于教材编辑检查。

新增三组图由 figures/gen_final_case_figures.py 原创生成。两幅流程图按实际代码组织，耗时图读取保存的运行数据，保留 SVG、PDF、300 DPI PNG。传感器桥接复用模拟实验预测，10 cm 为演练阈值；S01 为虚构手册，模型决策为离线回放，结果停在等待批准。
''')]:
    p=ROOT/filename;t=p.read_text(encoding='utf-8')
    if heading not in t:p.write_text(t.rstrip()+'\n\n'+content.strip()+'\n',encoding='utf-8')

(ROOT/'projects/README.md').write_text('''# 五个模型与检索项目的运行索引

在教材根目录使用 Python 3.11 或 3.12，先安装 `python -m pip install -r requirements-projects.txt`。教材原训练记录使用 Python 3.12、CPU、PyTorch 2.5.1；具体依赖版本见 requirements 文件。训练耗时随设备变化。

| 章节 | 单独运行命令 | 数据来源 | 主要输出（projects/results） |
|---|---|---|---|
| 22 | `python projects/run_projects.py --project bike` | UCI 单车公开数据，首次运行需要下载 | bike.npz、bike.pt |
| 23 | `python projects/run_projects.py --project digits` | scikit-learn 内置 8×8 数字 | digits.npz、digits.pt |
| 24 | `python projects/run_projects.py --project sensor` | 程序生成的模拟轨迹 | sensor.npz、sensor.pt |
| 25 | `python projects/run_projects.py --project segmentation` | 程序生成的模拟缺陷 | segmentation.npz、segmentation.pt |
| 31 | `python projects/run_projects.py --project retrieval` | 作者虚构设备手册与 15 个问题 | retrieval.npz、retrieval_index.joblib |

运行 `python projects/run_projects.py` 会顺序运行全部五项。单项运行只更新对应数据、模型与 metrics.json 中的项目条目；每次运行的环境记录在 project_environments.json。再次运行同一项目会覆盖它的原输出，若要保留随书记录，请先复制项目目录到自己的实验目录。

`python projects/verify_results.py` 从保存文件重新计算指标、检查划分与模型重载。先按相应章节的“项目运行路径”核对输出，再只改一个参数，例如学习率、窗口长度或检索候选数。不同实验应使用单独目录并记录修改值。

传感器结果还可接入 `python agent_projects/sensor_bridge.py`，阅读第 42.9 节观察预测、规则、工具与任务状态的衔接。Agent 三项项目和 DeepSeek 综合案例分别见 agent_projects/README.md 与 case_study/lungsight/README.md。
''',encoding='utf-8')
print('Synchronized metadata and project/source documentation.')
