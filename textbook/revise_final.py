"""Apply the reviewed final-edition editorial changes once, keeping an audit trail."""
from pathlib import Path
import json, re, hashlib

ROOT = Path(__file__).resolve().parent
LOG = ROOT / 'final_revision_log.json'
if LOG.exists():
    raise SystemExit('Editorial pass already applied; edit the canonical chapters for further corrections.')
chapters = {n: (ROOT / f'新版章节/{n:02}.md').read_text(encoding='utf-8') for n in range(1,45)}
before = dict(chapters)
edits = []

def replace(n, old, new):
    assert chapters[n].count(old) == 1, (n, old[:90], chapters[n].count(old))
    chapters[n] = chapters[n].replace(old, new, 1)
    edits.append({'chapter':n, 'kind':'correction', 'before':old, 'after':new})

def at_section(n, section, text, end=False):
    pattern = rf'(?m)^### {re.escape(section)} [^\n]+\n'
    m = re.search(pattern, chapters[n]); assert m, (n,section)
    position = m.end()
    if end:
        following = re.search(r'(?m)^### ', chapters[n][position:])
        position = position + following.start() if following else len(chapters[n])
    chapters[n] = chapters[n][:position].rstrip()+'\n\n'+text.strip()+'\n\n'+chapters[n][position:].lstrip()
    edits.append({'chapter':n,'section':section,'kind':'addition','text':text})

replace(1, r'+\lambda R(\theta)\right].', r'+\lambda\Omega(\theta)\right].')
at_section(1,'1.3',r'本书统一用 \(\Omega(\theta)\) 表示正则项，用 \(R(\theta)\) 表示第 4.5 节的总体风险。前者是人为加入训练目标的约束，后者是模型在目标分布上的平均损失，阅读时可以据此区分。',end=True)
replace(4,'假设模型对每个标签给出概率 \\(p_\\theta(y_i\\mid x_i)\\)，希望观测数据在模型下尽可能可能：',
        '在给定输入后各标签条件独立的建模假设下，模型对每个标签给出概率 \\(p_\\theta(y_i\\mid x_i)\\)。极大似然选择使观测数据的似然尽可能大的参数：')
replace(30,'下一章之后的高效训练部分会解释这些开销','第 27 章的高效训练与部署部分解释了这些开销')
replace(28,'### 28.3 四个逐步推进的项目','### 28.3 四项逐步推进的拓展练习')
for old,new in [('项目一','拓展练习 A'),('项目二','拓展练习 B'),('项目三','拓展练习 C'),('项目四','拓展练习 D')]:
    replace(28,'**'+old+'：','**'+new+'：')
replace(30,'### 30.8 实际检查结果：拟合成功还不够','### 30.8 实际检查结果：拟合、因果掩膜与重载')
at_section(44,'44.1',r'符号补充：\(\Omega(\theta)\) 为正则项；\(R(\theta)\) 为总体风险；\(\widehat R_n(\theta)=\frac1n\sum_i\ell(f_\theta(x_i),y_i)\) 为经验风险。优化目标常写成 \(\widehat R_n+\lambda\Omega\)。',end=True)

# Short, varied reading cues keep the original derivations in place.
for n,section,text in [
 (3,'3.8','**进阶选读。** 首次阅读先掌握第 3.1—3.6 节的轴、矩阵乘法和形状核对。本节先记住“用较少的独立方向近似原矩阵”，即可继续读第 3.9 节；学习第 27 章压缩或第 29 章 LoRA 时，再回来理解分解式。'),
 (4,'4.6','**首次阅读目标：会更新一次参数。** 先掌握第 4.1、4.2 节，能解释学习率和链式法则。下面的一阶近似帮助理解方向；二阶项与 Hessian 属于进阶选读。Hessian 是把各参数的二阶偏导数排成的矩阵，描述梯度随位置怎样变化。'),
 (4,'4.7','**推导选读。** 第一遍读到“固定高斯噪声对应平方误差”即可把它与回归任务联系起来。若想知道损失中的系数和对数项来自哪里，再逐行完成本节推导。'),
 (7,'7.8','**进阶选读。** 第 7.1—7.5 节已经构成完整训练步；首次阅读可先完成那一部分。雅可比矩阵把“每个输出对每个输入的偏导数”排成一张表。本节用这张表解释多个类别为什么相互影响，适合在熟悉第 8 章的 Softmax 后回读。'),
 (16,'16.1','**阅读顺序。** 先把注意力看成“按匹配程度分配权重，再汇总信息”，跟着小数字算例走一遍。第一遍重点是 Q、K、V 的角色与输出形状；多头、位置编码和复杂度可以在读第 30 章代码时再逐项对照。'),
 (29,'29.1','本章先沿“文本变成编号—预测下一个 token—训练与使用”这条线阅读。微调与偏好优化可以在理解基本目标后再读；代码细节接第 30 章，外部资料的使用接第 31、35 章。'),
 (43,'43.1','**按需进阶。** 先完成第 40—42 章中的一个单 Agent 项目，再阅读本章。这里的学习目标是判断何时分工有收益，以及怎样核算协调成本。')
]: at_section(n,section,text)

# Immediate checks: a short question, a calculation or a code change with explanation.
exercises = [
 (3,'3.4',r'**停下来核对。** 预测为 \([2,1]\)，标签为 \([2]\)，相减后是什么形状？先把标签补写成 \([1,2]\)，便得到 \([2,2]\)：每个预测与两个标签都相减。将标签显式变为 \([2,1]\)，才恢复两个样本各自配对。常见错误是只数元素个数，而没有核对轴。'),
 (4,'4.1',r'**手算一步。** 对 \(L(w)=w^2\)，从 \(w=3\) 出发，学习率取 0.1。梯度为 6，更新后 \(w=2.4\)，损失从 9 降到 5.76。若误写成加上梯度，参数变为 3.6，损失为 12.96；用这个对照检查更新符号。'),
 (6,'6.1',r'**解释一句话。** 已知 \(z=2w+1\)、\(L=z^2\)，在 \(w=1\) 时梯度是多少？先算 \(z=3\)，再算 \(dL/dw=2z\times2=12\)。漏掉最后的 2，就是只计算了损失对中间量的导数。'),
 (8,'8.1',r'**小练习。** 真类概率从 0.5 提高到 0.8，单样本交叉熵从约 0.693 降到 0.223。使用自然对数计算这两个值，并解释为什么负号使“概率越高”对应“损失越低”。'),
 (13,'13.1',r'**把结果算出来。** 一个 \(5\times5\) 输入使用 \(3\times3\) 卷积核，步长 1、不填充，输出为 \(3\times3\)。每边填充 1 后输出为 \(5\times5\)。可以在纸上数卷积核左上角的合法位置，检查是否把“核覆盖几个格子”误当成“核能移动几次”。'),
 (16,'16.2',r'**试着改一个权重。** 三个值为 2、4、10，权重为 0.2、0.3、0.5，汇总为 6.6。把最后一个权重减到 0.4、把第一个增到 0.3，汇总变为 5.8。输出减少 0.8，来自把 0.1 的权重从 10 移到 2；这就是加权汇总的可计算含义。'),
 (20,'20.1',r'**先写分母。** 系统报出 8 个正例，其中 6 个正确；数据中实际有 10 个正例。精确率是 \(6/8=0.75\)，召回率是 \(6/10=0.6\)。把“报出来的”与“实际存在的”分别写在分母旁，就不容易混淆两个指标。'),
 (31,'31.4',r'**手算排名。** 三个问题的首个相关文档分别排在第 1、2、4 位，则 Recall@1 为 \(1/3\)，Recall@3 为 \(2/3\)，MRR 为 \((1+1/2+1/4)/3=7/12\)。MRR 中没有在预定搜索范围内找到的题记为零，并继续计入总题数。'),
 (34,'34.3','**读一次返回结果。** 工具返回 `{"ok": false, "error": "version mismatch"}` 时，下一步应重新核对版本，再决定是否查询；最终回答应反映实际执行状态。把失败结果直接当作正文证据，会把程序状态与业务内容混在一起。'),
 (38,'38.5','**辨认两种检查。** 引文写“R2 本机保存 30 天”，回答却写“所有型号保存 30 天”。原文匹配检查通过，范围核对失败。给答案增加一列“对象与条件”，比重复检查引文是否存在更接近这道题的错误原因。')
]
for n,section,text in exercises: at_section(n,section,text,end=True)

application_tasks = {
18:'**读后小任务。** 把条件生成写成三个空格：“已知输入—逐步更新的对象—输出”。在分子结构案例中，依次填入分子组成等条件、带噪结构表示、预测三维结构；再与图像扩散的文本条件、带噪图像和生成图像对照。比较的重点是共同的条件生成过程。',
20:'**读后小任务。** 假设五条教学天气轨迹给出的最高温分别为 29、31、33、30、32℃，其中两条超过 31℃，集合估计的超阈值比例为 2/5。若问题改成“达到或超过 31℃”，比例为 3/5。再想一想：一次观察到高温，和多次预报的概率校准，分别需要怎样的数据？',
25:'**读后小任务。** 真值掩膜有 6 个前景像素，预测也有 6 个，交集为 4 个。IoU 为 4/8=0.5，Dice 为 8/12≈0.667。连续两帧即使得到相同 IoU，目标编号也可能交换；视频任务还需要核对跨帧身份。',
31:'**读后小任务。** 从本书虚构手册中选两段资料，分别写成一句问答和三句讲解提纲。给每个事实标上原文编号。表达形式改变了，事实与出处的对应关系仍应保留。',
32:'**读后小任务。** 把“移动到杯子旁”拆成一次观察、一个动作和再次观察，指出哪一步能发现杯子已经被移走。答案是动作后的新观察；只重读原始指令无法更新环境状态。',
34:'**读后小任务。** 在纸上设计一个返回两数之和的函数测试：输入 2 与 3，应得到 5。若候选程序返回 6，执行结果就提供了下一轮修改依据。记录输入、预期值、实际值即可复查这个失败。',
38:'**读后小任务。** 比较两个排序候选：先检查它们对相同列表都返回正确结果，再比较同一环境下的运行时间。若一个候选更快却漏掉重复元素，应先判正确性失败。速度评分只在满足任务定义后进行。'
}
for n,text in application_tasks.items():
    mark='<!-- /APPLICATION -->\n\n<!-- /BEGINNER -->'
    replace(n,mark,mark+'\n\n'+text)

starts={
22:('bike','projects','公开 UCI 日级单车记录；本包已有压缩文件时直接复用。','bike.npz、bike.pt 与 metrics.json 中的 bike 项。','核对测试集 124 天；先比较前一天、前一周与岭回归，再查看三个随机种子的 MLP。','先只修改 bikes() 内岭回归 alpha 的候选列表，并保持时间划分不变。'),
23:('digits','projects','scikit-learn 自带的 8×8 手写数字；无需另找图片。','digits.npz、digits.pt 与 metrics.json 中的 digits 项。','测试集为 360 张；先检查混淆矩阵计数总和，再复算准确率。','首次可把 digits() 中训练轮数从 45 改为 10，观察训练不足时的曲线。'),
24:('sensor','projects','脚本按固定种子生成含尖峰与缺失的模拟距离轨迹，单位为 cm。','sensor.npz、sensor.pt 与 metrics.json 中的 sensor 项。','测试含 20 段轨迹、1620 个窗口；同时比较 MAE 和 RMSE。','先调整模拟器中的尖峰概率，分别检查中值滤波与 CNN 的变化；保留原始结果作参照。'),
25:('segmentation','projects','脚本生成模拟划痕图及像素掩膜。','segmentation.npz、segmentation.pt 与 metrics.json 中的 segmentation 项。','测试为 100 张图；IoU、Dice 使用全局像素汇总，阈值由验证集选择。','先查看保存的 prob，尝试不同阈值对掩膜的影响；正式比较仍按验证集选阈值。'),
31:('retrieval','projects','12 段虚构设备说明与 15 个已写明目标文档的问题。','retrieval.npz、retrieval_index.joblib 与 metrics.json 中的 retrieval 项。','对照 truth 与 ranks，复算 Recall@1、Recall@3 和 MRR。','先把字符 n-gram 范围由 (2,3) 改为 (1,2)，逐题查看排名变化。'),
40:('knowledge','agent_projects','内置六段虚构、带版本号的手册；默认使用固定模型回放。','knowledge_trace.json 与 offline_results.json 中的 knowledge 项。','应有 3 个模型回合、2 次工具调用；最终引文来自实际读取的 K01。','先运行 test_projects.py 中的版本与引文测试，再在单独副本中修改手册。固定回放答案不会随资料自动改写。'),
41:('analysis','agent_projects','脚本准备 13 行教学订单，包括退款、重复和缺失记录。','analysis_trace.json、orders_report.md 与 offline_results.json 中的 analysis 项。','接受 10 行；总收入 1470、成本 913、利润 557。金额按十进制计算。','先修改 CSV_TEXT 中一条订单的成本，重跑后核对地区与总利润的相应变化。'),
42:('workflow','agent_projects','脚本在临时 SQLite 数据库内创建教学工单，关闭后自动清理。','workflow_trace.json 与 offline_results.json 中的 workflow 项。','检查 checkpoint_restored=true、重复操作 replayed=true、events=1。','先运行过期批准和陈旧版本两项测试，观察事务怎样保留原状态。')
}
for n,(project,folder,data,outputs,verify,first_change) in starts.items():
    prefix='完成第 21 章的 Python 环境准备，并安装 requirements-projects.txt。' if folder=='projects' else '使用 Python 3.12 标准库即可。'
    text=f'''**动手入口。** {prefix}以下命令均在教材根目录执行，只运行本章项目。数据：{data}

~~~powershell
python {folder}/run_projects.py --project {project}
~~~

结果写入 `{folder}/results/`：{outputs}单项目运行只更新该项目的结果条目，其他项目记录保留。核对顺序：{verify}

**第一次改动：** {first_change}改动前复制对应结果到自己的实验目录，并记录参数；本书表格对应随包保存的基准运行。
'''
    first=re.search(r'(?m)^### ([\d.]+) ',chapters[n])[1]
    # Place before the first section without changing its section number.
    position=chapters[n].index('### '+first+' ')
    chapters[n]=chapters[n][:position]+text+'\n'+chapters[n][position:]
    edits.append({'chapter':n,'kind':'project_entry','project':project,'text':text})
replace(40,'python agent_projects/run_projects.py\npython agent_projects/test_projects.py','python agent_projects/run_projects.py --project knowledge\npython agent_projects/test_projects.py')
replace(40,'第一条命令运行三个 Agent 项目的离线回放；第二条运行工程测试。','第一条命令运行知识库项目的离线回放；第二条运行工程测试。')
replace(40,'python agent_projects/run_projects.py --live','python agent_projects/run_projects.py --project knowledge --live')
replace(41,'python agent_projects/run_projects.py\n','python agent_projects/run_projects.py --project analysis\n') if chapters[41].count('python agent_projects/run_projects.py\n')==1 else None

# Remove repetitive defensive phrasing while retaining concrete technical conditions.
tone_changes={
30:[('这是代码与拟合实验，没有独立泛化测试。','本实验检查代码计算和固定序列拟合；泛化实验使用另外冻结的独立序列。')],
38:[('哈希用于比较内容是否一致，不是对业务正确性的证明；同时应保留受控的原始结果以便复查。','哈希用于比较内容是否一致；业务正确性由任务验收器检查，原始结果随轨迹保存以便复查。')],
40:[('查询与文档没有共同二元组时返回空列表，程序不能把“空列表”解释成世界上不存在答案，只能说当前检索没有找到。','查询与文档没有共同二元组时返回空列表，状态应记为“当前检索未找到”，然后选择改写查询、补充资料或结束查找。'),('这些检查能阻止虚构编号、引用未读资料和伪造引文，但它不验证答案是否被引文逻辑支持。','这一层检查编号、读取记录和引文原文；下一层检查答案中的事实、对象与适用条件。'),('它是特意留下的能力边界：工程核验做到了来源存在性，却没有完成所有事实与范围判断。','它对应第二层验收：逐项核对事实与适用范围。')]
}
for n,pairs in tone_changes.items():
    for old,new in pairs:
        if old in chapters[n]:replace(n,old,new)

for n,text in chapters.items():
    (ROOT/f'新版章节/{n:02}.md').write_text(text,encoding='utf-8')
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
patterns={'display_math':r'\$\$([\s\S]*?)\$\$','inline_math':r'\\\(([\s\S]*?)\\\)','code_blocks':r'~~~[^\n]*\n([\s\S]*?)~~~'}
record={'edition':'final','keep_programming_intro_chapter':21,'changes':edits,
        'before_chapter_sha256':{str(n):digest(s) for n,s in before.items()},
        'after_editorial_chapter_sha256':{str(n):digest(s) for n,s in chapters.items()},
        'before_entries_sha256':{k:[digest(s) for s in re.findall(p,'\n'.join(before.values()))] for k,p in patterns.items()},
        'author_config_sha256':hashlib.sha256((ROOT/'author_page.json').read_bytes()).hexdigest()}
LOG.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'editorial_changes':len(edits),'chapters_changed':[n for n in chapters if chapters[n]!=before[n]],'programming_intro_kept_at':21},ensure_ascii=False))
