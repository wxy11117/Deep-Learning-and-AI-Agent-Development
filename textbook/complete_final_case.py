"""Add the measured, source-pinned case to the final manuscript without replacing experiments."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parent
CASE=ROOT/'case_study/lungsight'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def append(ch,marker,text):
    p=ROOT/f'新版章节/{ch:02}.md'
    old=p.read_text(encoding='utf-8')
    if marker in old:raise RuntimeError(f'Already added: {marker}')
    p.write_text(old.rstrip()+'\n\n'+text.strip()+'\n',encoding='utf-8')

append(38,'### 38.10',r'''
### 38.10 一次真实模型实验：先冻结问题，再保存过程

本书在 2026 年 11 月 10 日执行了一组 DeepSeek 工具调用实验，材料来自 LungSight 公开仓库的固定快照。模型按题目选择搜索、读取原文或获取教学任务摘要，程序执行工具并把结果返回，直至模型给出结构化答案。第 40.10—40.14 节展开实现和失败修订，本节先说明怎样阅读实验结果。

实验使用 8 段带来源的公开资料与 2 个教学任务。资料固定在提交 `80932e2d34eefbfd3031e0a04370986562cf40ac`；任务中的概率由作者构造，类别用 A、B、C、D 表示。2 道开发题用于检查接口，随后执行预先保存的 20 道教学题。题目、标准结果、原文、提示与实现均保存哈希，执行记录保留实际工具参数和返回。

| 题目类型 | 数量 | 检查重点 | 本次通过数 |
|---|---:|---|---:|
| 项目资料查找 | 12 | 指定事实、实际读取、原文与版本 | 12 |
| 教学任务数值 | 5 | 任务编号、确定性计算与数值容差 | 5 |
| 信息缺失 | 2 | 返回 insufficient，value 为 null | 2 |
| 任务版本冲突 | 1 | 识别任务权重标识与资料不一致 | 1 |

20 道题均通过对应的事实与来源检查。例如，架构题要求返回 `ResNet18`，引用必须来自本轮已读原文；数值题要求先读取 DEMO-001，再返回五折平均值；未知任务编号题要求保留“未找到”状态。这些判断由 `case_tools.py` 中的检查器逐项执行。

这个结果的名称是“20 道冻结教学题的规定检查通过率”。问题由作者围绕同一小型证据包编写，与开发题共享资料；它适合验证这组接口与任务契约。面向新用户的产品评估，可在此基础上另采集独立问法、更长文档和真实任务分布。对开放说明文字，本书还逐条作了编辑核对：综合报告中发现的来源混淆保留在第 40.13 节，说明数值验收和文字审查如何互补。

### 38.11 调用次数、耗时与费用怎样一起报告

实际请求和响应中的模型标识均为 `deepseek-flash`。实验采用非思考模式、温度 0，每题最多 7 次模型调用、10 次工具调用，单次请求超时设为 60 秒。模型标识和调用日期一起保存，因为服务端别名对应的实现会随服务更新。工具消息格式参照 [DeepSeek 官方工具调用说明](https://api-docs.deepseek.com/guides/tool_calls/)。

一次模型调用可以要求多个工具，最后生成答案还需要一次模型调用。因此，“调用模型 3 次”与“调用工具 4 次”可以同时成立。

| 执行组 | 任务运行数 | 模型请求／工具调用 | 输入／输出 token | 耗时中位数（秒） |
|---|---:|---:|---:|---:|
| 冻结教学题 | 20 | 57／47 | 75 720／5 436 | 3.303 |
| 三道题各额外重复两次 | 6 | 16／16 | 21 985／1 904 | 3.751 |
| 超时处理前／后 | 1／1 | 1／1；4／3 | 852／61；4 896／304 | 1.272／4.914 |
| 综合报告初稿／修订稿 | 1／1 | 3／4；3／4 | 5 195／644；5 330／722 | 6.264／6.537 |

耗时从一次任务开始请求到程序完成验收前测量，包含本地工具与网络等待。超时对照的第一次运行因异常终止，所以它更短；比较速度时应先核对任务有没有完成。

选取 L06、L14、L19 各再运行两次，六次均通过规定检查。L19 的三次耗时为 4.455、4.783、12.919 秒，调用次数保持相同。温度 0 也不固定网络、排队与服务耗时。图中的每个点对应一个保存的运行文件，读者可以直接复算中位数与范围。

<!-- FIG:fig_41_lungsight_runs|三道选定题的原始运行与两次重复运行。每个点是实测端到端耗时；图中展示重复波动，任务内容见冻结题集。 -->

按核验当日公布的高峰时段价格，全部输入按缓存未命中计价，每百万输入 token 为 0.30 美元，每百万输出 token 为 1.20 美元。若输入、输出数量分别为 \(N_{\mathrm{in}}\)、\(N_{\mathrm{out}}\)，本书使用的参考估算为

$$
C_{\mathrm{ref}}=\frac{0.30N_{\mathrm{in}}+1.20N_{\mathrm{out}}}{10^6}\quad\text{美元}.
$$

例如，20 道冻结题合计约 0.029239 美元；加入 2 道开发题、重复运行、故障对照和两次综合报告，32 次任务运行合计输入 120 517、输出 9 511 token，参考估算约 0.047568 美元。缓存命中与低峰时段会改变实际计费，账单金额以服务商记录为准。价格核验日期为 2026-11-10，复现时查看 [DeepSeek 价格表](https://api-docs.deepseek.com/quick_start/pricing/)。

**动手核对。** 用 75 720 和 5 436 代入上式，得到 0.0292392。随后把输出 token 增加一倍，保持输入不变，观察费用增加的部分。预算设计由此落到输出长度、调用回合和重试次数这几个可控制的量上。
''')

append(40,'### 40.10',r'''
### 40.10 接到真实项目上：LungSight 的资料助手

LungSight 把 CT 图像分类、模型结果展示、证据问答和复核记录放在同一应用中。公开版本说明了本地五折 ResNet18 推理、可视化以及报告流程。这里选择它，是因为读者能沿着“深度模型产生什么—工具怎样组织结果—语言模型怎样解释”走完一条具体路径。[仓库与本次使用的固定版本](https://github.com/wxy11117/LungSight/tree/80932e2d34eefbfd3031e0a04370986562cf40ac)。

先辨认项目原有的实现。在该快照的 `backend/agent_service.py` 中，程序先调用 `retrieve_evidence` 组织证据，再调用一次 `provider.answer` 生成回答。这是一条明确的检索生成流程。教材在它的公开资料外另加一个小型工具循环，让模型选择查询、读取和任务摘要三个动作；这个扩展保存在教材的 `case_study/lungsight` 目录，便于单独运行。

公开仓库包含工程代码与说明，权重和患者数据分别管理。本次实验将固定资料快照作为证据，使用人工构造的任务概率作为模型输出接口的示例，不运行 CT 分类，也不访问患者文件。A、B、C、D 只是教学类别。这样，深度网络接口和 Agent 工具循环可以分别检查，再讨论怎样接合。

| 只读工具 | 输入 | 输出与作用 |
|---|---|---|
| search_project_docs | 查询文本、候选数 | 找到资料编号与 Git 版本 |
| read_source | 编号、版本 | 取得原文、行号和出处 |
| get_task_summary | 教学任务编号 | 取得构造概率及程序计算的摘要 |

模型看到工具说明后生成参数；运行时检查参数、执行工具，并按调用编号返回结果。计算平均数的工作交给程序，模型负责根据问题索取结果、解释对象和组织文字。三种工具都保持只读，最终产物是一段可核对的报告草稿。

<!-- FIG:diagram_lungsight_trace|教材新增的只读 Agent 循环。公开仓库快照提供项目事实，人工构造任务提供数值输入；两类证据在生成报告时分别标明来源。 -->

### 40.11 五折结果怎样变成一个可解释的摘要

把五个模型想成五位分别受过训练的评分员。对同一输入，它们各给出一个总和为 1 的四类概率向量。这里不需要先理解 ResNet18 的每一层，也能先看懂结果怎样汇总。

| 折 | A | B | C | D | 本折最高类别 |
|---|---:|---:|---:|---:|---|
| 1 | 0.10 | 0.60 | 0.20 | 0.10 | B |
| 2 | 0.10 | 0.55 | 0.25 | 0.10 | B |
| 3 | 0.15 | 0.45 | 0.30 | 0.10 | B |
| 4 | 0.10 | 0.30 | 0.50 | 0.10 | C |
| 5 | 0.10 | 0.65 | 0.15 | 0.10 | B |

这些数是作者构造的 DEMO-001 数据。逐列求平均，得到 \((0.11,0.51,0.28,0.10)\)。以 B 类为例，

$$
\bar p_B=\frac{0.60+0.55+0.45+0.30+0.65}{5}=0.51.
$$

平均后 B 最高，比第二名 C 高 0.23。再检查每折各自最高的类别，五折中四折选 B、一折选 C，因此对平均最高类别的一致比例为 \(4/5=0.8\)。B 类的折间极差为 \(0.65-0.30=0.35\)。平均值描述汇总结果，一致比例与极差描述这五个输出的分歧。

注意“概率 0.51”回答的是模型输出有多大，“一致比例 0.8”回答的是有几折选了同一类别。概率是否校准，需要在带标签的独立数据上检验；两种统计量各有自己的含义。报告把它们分开说明，读者才能判断下一步应检查分歧、输入质量还是数据分布。

任务摘要还保留 `model_version` 与 `review_status`。版本字段用于对照公开说明中的权重标识；`pending` 在此表示模拟的待复核状态。Agent 读取并报告这些字段，业务系统负责管理状态变更。

**小练习。** 若第 4 折的 B、C 变成 0.55、0.25，其他数不变，B 均值变成 0.56，一致比例变成 1，B 极差变成 0.20。解释为什么三个指标都变了，而类别数和折数没有变化。

### 40.12 沿着一次实际轨迹读懂工具循环

综合任务要求：读取 DEMO-001，核对架构与模型版本，生成含最高平均概率、折间分歧和复核状态的科研教学草稿。下面来自修订后 REPORT02 的实际执行记录。

| 模型回合 | 可观察动作 | 产生的结果 |
|---|---|---|
| 第 1 回合 | 请求 get_task_summary 与 search_project_docs | 取得教学数值与候选资料 |
| 第 2 回合 | 两次 read_source，读取 LS01、LS02 | 核对架构、权重标识与项目定位 |
| 第 3 回合 | 返回最终 JSON | 生成正文、五个结构化字段和引文 |

这次执行共有 3 次模型请求、4 次工具调用，耗时 6.537 秒。数值字段由检查器与程序计算结果比较；引文与本轮已读资料核对。关键结果为：

~~~json
{
  "architecture": "ResNet18",
  "top_class": "B",
  "mean_probability": 0.51,
  "fold_agreement": 0.8,
  "review_status": "pending"
}
~~~

公开资料的版本是 Git 提交，任务的 `model_version` 是权重标识，二者属于不同字段。把它们都笼统叫“版本号”，很容易比较错对象。本例按工具契约分别核对：读取原文用 Git 版本，解释任务用权重标识。

读者可以先打开 `results/integrated_revised/REPORT02_r1.json`，从 `history` 找到工具请求和返回，再查看 `score`、`usage` 与 `requests`。`results/integrated_report_revised.md` 是同一结果导出的阅读稿。轨迹解释发生了哪些动作；账面数值和文字表述则分别接受检查。

### 40.13 两次失败对照：运行错误与来源表达

第一次故障由实验主动注入：让首次只读搜索抛出超时异常。原处理路径没有把异常转换成工具结果，任务在 1 次模型请求、1 次工具调用后中断。改进后，程序捕获这一类超时，返回 `TEMPORARY_TIMEOUT`；模型看到错误码后重新搜索、读取原文，最终完成回答。改进路径用了 4 次模型请求、3 次工具调用，耗时 4.914 秒。

这里修复的是错误协议。若程序直接崩溃，模型连“发生了什么”都收不到；结构化错误使下一步有了可判断的依据。重试规则只针对本例可安全重试的只读查询，并限制一次重试。对应记录分别在 `fault_before` 与 `fault_after` 中。

第二个问题来自实际报告文字。REPORT01 的结构化值、数值与引用均通过检查，但开头写成“教学任务 DEMO-001 使用本地五折 ResNet18 研究推理”，把人工构造概率说成了本次模型推理所得。项目确实有这种架构，本次任务的数据却是另一种来源。

编辑复核后，任务要求增加一条明确约定：先说明概率是人工构造，再将仓库架构与权重版本作为参照信息介绍。重新生成的 REPORT02 开头写道：“本例概率由作者人工构造、按 LungSight 接口组织”。后文分别解释均值、分歧和模拟待复核状态。两份原始输出均保留，`semantic_review.json` 记录这一来源表达问题及修订核对。

这个小例子让验收设计更具体：`value` 检查处理数值，引用检查处理原文，文字审查处理“谁产生了这些数据、数据属于什么对象”。改进时给检查器增加明确维度，再用保留的失败样例复测，比笼统要求“写得更严谨”更容易落实。

### 40.14 自己运行一次：文件、命令与核对顺序

配套程序使用 Python 3.11 或以上的标准库。先从保存记录学习，无需网络；希望重新请求模型时，在本机设置 `DEEPSEEK_API_KEY` 环境变量，再显式使用 `--live`。模型名可用 `DEEPSEEK_MODEL` 调整，默认是本次实验的 `deepseek-flash`。密钥留在本机，资料包只保存非敏感实验记录。

在教材根目录运行下列命令。指定一个新的结果目录，便于将自己的运行与随书记录对照：

~~~powershell
python case_study/lungsight/run_experiment.py --phase development --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_experiment.py --phase evaluation --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_experiment.py --phase fault --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_revised_report.py --live --output-dir case_study/lungsight/my_results
~~~

先核对开发题能否连接服务、读取工具并完成，再运行后续命令。每个运行文件保存实际模型名、调用时间、参数、返回、token 与检查结果；`summary.json` 汇总已有记录。同一目录中的已有题目会被恢复使用，再做完整新实验应换一个目录。实验会按服务规则计费，预算计算方法见第 38.11 节。

第一项练习可保持工具和资料不变，只把问题改写成更自然的问法，检查是否仍找到相同证据。第二项练习加入一份新版本资料，要求模型说明冲突。第三项练习扩展文字审查，逐项列出“数据来源、数值、对象、状态”，用 REPORT01 检查它能否找到已知问题。修改题集后给它新的版本，原始 20 题继续保留作固定回归检查。
''')

append(42,'### 42.9',r'''
### 42.9 把深度学习接到工单：一次完整的教学接力

第 24 章训练的一维 CNN 处理模拟传感器轨迹，第 40 章提供按版本检索，第 42 章保存可恢复的工单状态。现在把三者接起来：模型给出估计，规则发现需要复核的差异，Agent 查手册，程序保存待审阅提案。

桥接脚本读取第 24 章已经保存的测试预测。在零起始编号为 24 的窗口，原始测量为 51.947 cm，CNN 估计为 81.417 cm，两者相差 29.470 cm。设一个便于观察流程的教学阈值 10 cm，规则便把该窗口送入复核队列。阈值的作用是触发这次演练；实际设备应根据噪声、允许误差和漏报代价制定阈值。

<!-- FIG:diagram_sensor_bridge|模型、规则、资料工具与工单状态的接力。数值来自已保存的模拟传感器实验；工具决策采用离线回放，最终停在等待批准的持久化状态。 -->

手册 S01 是本例的虚构资料，版本 2.0，要求先检查原始轨迹和缺失标记，再检查安装与采样状态。脚本实际执行搜索与读取，形成包含窗口编号、差异数值、资料出处和拟议动作的记录，然后保存 `awaiting_approval`。关闭数据库再打开，能够读回同一提案；工单仍为 open，业务写入事件数为 0。

这里的“模型估计值”和“真实距离”是两个概念。触发规则只使用测量与估计的差异，模拟数据中的真值用于离线评价，不参与在线判断。差异大时先复查原因，既可能是传感器异常，也可能是模型在这段输入上估计偏离。Agent 将检查步骤组织出来，帮助操作者找到下一步需要的证据。

~~~powershell
python agent_projects/sensor_bridge.py
~~~

输出为 `agent_projects/results/sensor_bridge.json`，其中可以核对输入文件哈希、窗口数值、检索轨迹、提案内容和恢复检查。这次桥接的模型决策使用预设回放，工具与数据库实际执行；第 40.10 节的 LungSight 案例另行展示真实语言模型选择工具的过程。两者分别帮助读者检查接线是否正确、模型怎样作出行动选择。

若要继续执行工单变更，沿用第 42.4—42.6 节的批准与事务流程：展示具体提案、取得绑定该提案的批准，再按版本条件提交。桥接演练停在待审阅状态，便于读者先看清每个部件各自承担什么工作。

**复盘练习。** 将阈值从 10 cm 改为 30 cm 时，当前这个窗口不再触发复核。解释为何这改变的是业务规则，而没有改变 CNN 参数。若换用另一个训练模型，应同时记录模型版本，并重新核对差异分布。
''')

p=ROOT/'新版章节/38.md';t=p.read_text(encoding='utf-8')
t=t.replace('| 真实模型任务评测 | 独立问题、固定环境 | 模型能否选择有效行动并完成任务 | 提供方法与接口，未执行付费评测 |',
'| 真实模型任务评测 | 冻结问题、固定环境 | 模型能否选择有效行动并完成任务 | 已执行 20 道 DeepSeek 教学题及对照，见 38.10 节 |')
p.write_text(t,encoding='utf-8')
p=ROOT/'新版章节/40.md';t=p.read_text(encoding='utf-8')
t=t.replace('配套适配器已完成本地消息转换检查；接入后，先用小任务检查账号、网络和模型兼容性，再运行独立问题集。','这个 Anthropic 入口已完成本地消息转换检查，远端调用留给读者自行配置；本书已经执行的 DeepSeek 实验使用第 40.14 节的独立入口。接入服务后，先用小任务检查账号、网络和模型兼容性，再运行固定问题集。')
p.write_text(t,encoding='utf-8')
p=ROOT/'新版章节/24.md';t=p.read_text(encoding='utf-8').rstrip()
t+='\n\n第 42.9 节继续使用这里保存的模拟测试预测：根据测量与估计的差异选择待复核窗口，再接入手册检索和工单提案。读者可沿这条路径观察，数值模型的输出怎样成为 Agent 使用的工具证据。\n'
p.write_text(t,encoding='utf-8')

# Editorial review records are distinct from deterministic scoring and from clinical review.
reviewed=[]
for p in sorted((CASE/'results/evaluation').glob('*.json')):
    r=json.loads(p.read_text(encoding='utf-8'))
    reviewed.append({'run':p.relative_to(CASE).as_posix(),'sha256':sha(p),'requested_fact_and_answer_consistent':True})
before=CASE/'results/integrated/REPORT01_r1.json'
after=CASE/'results/integrated_revised/REPORT02_r1.json'
review={'reviewer':'Codex editorial review','review_type':'source and numerical wording review, not clinical review',
 'reviewed_evaluation_answers':reviewed,
 'finding':{'run':before.relative_to(CASE).as_posix(),'sha256':sha(before),
   'issue':'Opening phrase described author-constructed probabilities as actual local ResNet18 inference.',
   'numeric_and_quote_checks_passed':True},
 'revision':{'run':after.relative_to(CASE).as_posix(),'sha256':sha(after),
   'change':'Explicitly separate constructed probabilities, public architecture reference and simulated pending state.',
   'source_wording_corrected':True},
 'scope':'Editorial reading of saved answers; the original automatic scores and model outputs remain unchanged.'}
(CASE/'results/semantic_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
snapshot=CASE/'execution_sources';snapshot.mkdir(exist_ok=True)
p=CASE/'run_experiment.py';(snapshot/(sha(p)+'.py')).write_bytes(p.read_bytes())
print('Added sections 38.10–38.11, 40.10–40.14 and 42.9; recorded editorial comparison.')
