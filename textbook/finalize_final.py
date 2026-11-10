"""Package the verified final edition, excluding credentials and local dependencies."""
from pathlib import Path
import sys,json,hashlib,zipfile,re,datetime
from verify_publication import write_code_scope, verify_publication
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'_build_deps'))
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pdf=load('pdf_check.json');layout=load('layout_check.json');locations=load('page_locations.json')
source=load('source_check.json');preserved=load('content_preservation_check.json');beginner=load('beginner_check.json')
final_content=load('final_content_check.json');final_projects=load('final_project_checks.json')
author=load('author_page.json');core=load('agent_projects/results/verification.json');mcp=load('agent_projects/results/mcp_verification.json')
old=load('projects/results/verification.json');live=load('case_study/lungsight/results/summary.json')
visual=load('final_visual_review.json')
assert final_content['passed'] and final_projects['failed']==0 and beginner['passed']
assert all(preserved[k]['retained_or_corrected'] for k in ['display_math','inline_math','code_blocks','table_rows'])
assert layout['chapters']==44 and layout['figures']==68
assert all(pdf[k] for k in ['songti_embedded','heading_font_embedded','cover_font_embedded','kaiti_embedded','author_font_embedded','author_title_font_embedded'])
for k in ['empty_pages','outside_bounds','missing_section_references','page_label_errors','toc_page_mismatches','toc_link_mismatches','overview_page_mismatches','stamp_content_mismatches']:assert not pdf[k],(k,pdf[k])
assert pdf['overview_entries']==47 and pdf['toc_entries']==472
assert layout['katexErrors']==layout['overflows']==0 and not layout['printCheck']['overflows'] and not layout['printCheck']['oversizedFigures']
assert layout['mobile']['width']==layout['mobile']['scroll']==390
assert core['tests']==27 and core['errors']==core['failures']==0 and mcp['passed']==8 and old['passed']==26
assert visual['passed'] and visual['pages']==pdf['pages']
assert visual['pdf_sha256']==sha(ROOT/'深度学习与AI_Agent开发_精排版.pdf')
assert author['signature_size_pt']==28 and locations['locations']['author-page']['physical']==2
pages=pdf['pages'];figures=layout['figures'];today=datetime.date.today().isoformat()

guide=f'''# 深度学习与 AI Agent 开发：原理、实战与应用

修订版 · 完成日期 {today} · 作者 Violet、Star、Sapphire

本版共 {pages} 个 PDF 页面：封面 1 页、作者扉页 1 页、前置内容 {locations['front_pages']} 页（含版权页）、正文 {locations['body_pages']} 页、参考文献 {locations['reference_pages']} 页。44 章、{figures} 组正文图示、8 个基础项目、76 条参考文献，另有 LungSight 真实模型综合案例和传感器贯穿演练。保留 92 处零基础讲解与 7 个近年应用案例。

## 打开文件

在线阅读：[直接打开本书](https://wxy11117.github.io/Deep-Learning-and-AI-Agent-Development/)。

公开仓库：[Deep-Learning-and-AI-Agent-Development](https://github.com/wxy11117/Deep-Learning-and-AI-Agent-Development)。仓库的 `docs/` 提供在线阅读版与 PDF，`textbook/` 按原目录保存书稿、图示、项目与实验记录；完整离线资料包在 Releases 中下载。以下运行与构建命令均在教材根目录执行（仓库中为 `textbook/`，完整资料包中为解压目录）。教材正文与图表保留版权，原创代码采用 MIT，第三方资料遵循各自许可，详见版权页与仓库许可文件。

- `深度学习与AI_Agent开发_精排版.pdf`：正式阅读与打印版本；简明总目录、逐节详细目录、书签、内部跳转和分层页码。
- `深度学习与AI_Agent开发_阅读版.html`：图片、数学样式与字体内嵌的离线阅读版，含章节侧栏与手机布局。
- `深度学习与AI_Agent开发.md`：组装后的整书源稿。修改以 `新版章节/01.md`—`44.md` 为准，再运行组装脚本。
- `示例验证记录.md`：数值、项目、真实模型、正文与版式的检查结果。
- `修订说明.md`：本轮改动与保留事项。
- `版权页.md`、`作者与版本信息.md`：作者署名、版本与版权信息。
- `参考文献.md`、`publication/references.bib`：76 条规范著录及可导入文献管理器的记录，核验依据见 `publication/reference_audit.json`。
- `LICENSE.md`、`LICENSE-CODE.txt`：正文和图表保留版权；原创代码采用 MIT，具体文件及哈希见 `publication/code_license_scope.json`。
- `THIRD_PARTY_NOTICES.md`：字体、软件、数据及 LungSight 来源快照的权利和许可说明。

## 阅读路线

第一遍读第 1—12 章的概念与小算例，先学会核对形状、计算损失和更新参数。SVD、Hessian、Softmax 雅可比按“进阶选读”提示回读。第 13—20 章进入架构与评价，第 21 章仍负责 Python 与工程入门；随后按第 22—25 章单独运行项目。

语言模型路线为第 16 章注意力 → 第 29 章大语言模型 → 第 30 章迷你 Transformer → 第 31 章检索。Agent 路线为第 32—39 章概念、接口、循环、恢复与评价 → 第 40—42 章三个项目。第 38.10—38.11 节报告 DeepSeek 实验，第 40.10—40.14 节解释 LungSight 案例，第 42.9 节连接传感器预测、手册与工单。

## 单独运行项目

使用 Python 3.11 或 3.12。在教材根目录先执行 `python -m pip install -r requirements-projects.txt` 安装模型项目依赖。第一个公开单车数据项目首次运行需要下载数据；传感器、缺陷、手册、订单与工单均明确标注教学模拟或虚构来源。

```powershell
python projects/run_projects.py --project bike
python projects/run_projects.py --project digits
python projects/run_projects.py --project sensor
python projects/run_projects.py --project segmentation
python projects/run_projects.py --project retrieval
python agent_projects/run_projects.py --project knowledge
python agent_projects/run_projects.py --project analysis
python agent_projects/run_projects.py --project workflow
```

每次只选需要的命令。前五项入口见 `projects/README.md`，后三项只需标准库，见 `agent_projects/README.md`。再次运行同一项目会更新它的结果；另建实验目录便于保留随书记录。数值复核命令为 `python projects/verify_results.py`；工程检查为 `python agent_projects/test_projects.py` 和 `python agent_projects/test_mcp.py`。

真实模型案例见 `case_study/lungsight/README.md`。默认先阅读保存结果，重新调用需要本机凭据和显式 `--live`，并使用新的 `--output-dir`。API 按服务商规则计费；教材记录 token 与参考估算，密钥不在资料包中。

## 重新生成书籍

安装 `requirements-book.txt` 和 package.json 中的构建依赖，并准备 Chromium 或 Edge。以下命令在教材根目录运行：

```powershell
python assemble_revised.py
python prepare_fonts.py
python prepare_style_fonts.py
python figures/gen_final_case_figures.py
python verify_beginner_material.py
python verify_final_book_content.py
node build_book.mjs
python finish_layout.py
node build_book.mjs
python finish_layout.py
python check_revised.py
python verify_beginner_layout.py
node check_beginner_screen.mjs
python verify_publication.py
```

两轮构建同步目录页码。若 `pdf_check.json` 中仍有目录页码差异，重复构建、页眉页码、检查三步。视觉检查记录在 `final_visual_review.json`；改稿后应重新检查相关页面。完成所有检查后运行 `python finalize_revised.py` 更新指南、交付清单、预览与完整资料 ZIP。

字体沿用确认版式：正文宋体 12 pt，标题黑体，注记楷体，三位作者 Great Vibes 28 pt。Windows 宋体与楷体从系统读取；开放字体子集及许可随包提供。更换操作系统或字体后，重新核对分页。

资料包排除本机依赖、缓存、私有凭据和中间渲染文件。`validation_reference.json`、`final_revision_log.json` 与实验脚本哈希用于核对修订与实验，不是旧版成书。
'''
(ROOT/'阅读指南.md').write_text(guide,encoding='utf-8')

changes=f'''# 修订说明

完成日期：{today}。当前成书 {pages} 页、44 章、{figures} 组正文图示。

1. 编程入门保留在第 21 章。SVD、Hessian、Softmax 雅可比等位置增加首次阅读目标和进阶回读提示。
2. 八个项目集中补齐单独运行命令、数据与输出、核对方法、第一项修改练习。单项命令保持其他项目结果。
3. 关键概念与七个近年应用案例旁增加短练习和解释；不统一段落长度。
4. 纠正重复字、章节指向、拓展练习编号；正则项统一用 Ω，整体风险用 R。原公式、代码与表格按保留或明确修订核对。
5. 新增传感器—规则—手册—待审工单的贯穿演练，以及 LungSight 公开快照与构造任务的真实 DeepSeek 工具实验。
6. 保存 20 道冻结题、6 次重复、超时处理前后、综合报告来源表达修订前后；调用数、耗时、token 与估算费用均来自记录。
7. 增加简明总目录。保留封面创意、正文与标题字体、三位作者的顺序和 28 pt 署名字号。
8. 补入版权与作者信息页及 76 条参考文献，正文链接附引用编号；新增目录、书签与跳转。版权页保留版本年月，删除重复的“资料整理日期”一行。
9. 原创配套代码采用经确认的 MIT 许可，正文与图表保留版权；第三方内容单列来源和许可，LungSight 的 AGPLv3 截图作为许可参考，不改变其源仓库或快照的许可。
10. 资料说明、版权页、封面与交付清单统一为 68 组正文图示，补齐作者信息。
11. 增加公开仓库与在线阅读入口；版权页在第三方资料下方列出配套资料链接及许可衔接说明。

原深度学习项目保留训练产物，本轮重新复算指标与重载模型；没有重新训练所有模型。三个基础 Agent 项目继续使用离线回放，新增 DeepSeek 案例单独标明真实模型运行。报告中的构造概率、模拟数据与公开项目属性分别注明来源。

本版文件沿用稳定名称。工作区只以这套当前稿为正式交付，历史清理记录保留作操作记录。
'''
(ROOT/'修订说明.md').write_text(changes,encoding='utf-8')

group_rows=[]
names={'development':'开发题','evaluation':'冻结教学题','repeat':'追加重复','fault_before':'超时处理前','fault_after':'超时处理后','integrated':'综合初稿','integrated_revised':'综合修订稿'}
for key,g in live['groups'].items():
    group_rows.append(f"| {names[key]} | {g['runs']} | {g['passed']} | {g['model_requests']}／{g['tool_calls']} | {g['input_tokens']}／{g['output_tokens']} | {g['median_seconds']:.3f} | {g['estimated_usd_peak_cache_miss']:.7f} |")
record=f'''# 示例、内容与版式验证记录

本版交付检查日期：{today}。DeepSeek 实际调用日期：2026-11-10。

## 正文和版式

- {pages} 页，44 章，{figures} 组正文图示；源稿汉字 {source['cjk_chars']} 个。
- {layout['math']} 处数学表达，KaTeX 错误 0；桌面和 A4 宽度溢出 0；390 像素手机宽度无横向文档溢出。
- 简明总目录 47 项，详细目录 {pdf['toc_entries']} 项；印刷页码、链接目标、PDF 页标签已核对。
- 参考文献 76 条，BibLaTeX 结构检查无错误或重复；电子会议资料未提供的页码按官方记录留空，原因见 `publication/reference_audit.json`。
- 版权与作者信息、MIT 完整条款、第三方说明和代码许可范围清单均随包提供，出版资料检查见 `publication/publication_check.json`。
- 空白页、物理页面外文本、缺失章节引用和加页眉前后正文差异均为 0。
- 宋体、楷体、标题与封面黑体、Great Vibes、扉页书名字体均实际嵌入；正文 12 pt，作者署名 28 pt。
- 全书联系表与代表页逐页检查；具体页面与检查项见 final_visual_review.json。
- 92 处既有入门补充和 7 个应用案例保留，26 项入门手算与代码/JSON 片段核对通过。原独立公式、行内公式和代码按 final_revision_log.json 中的明确修订回溯检查。
- {final_content['total_checks']} 项本版内容核对通过，包括来源快照、题集哈希、费用与调用总量、项目入口、章号、作者页配置。

## 本地数值与工程检查

| 检查 | 通过数 | 实际内容 |
|---|---:|---|
| 模型项目复算与重载 | 26 | 保存模型、指标、划分与预测一致性 |
| Agent 核心工程 | 27 | 参数、预算、引文、恢复、事务、幂等与消息转换 |
| MCP 子进程集成 | 8 | 实际 stdio 进程、初始化、发现、工具与错误响应 |
| 本版项目专项 | {final_projects['passed']} | 单项目入口、其他结果保留、DeepSeek 消息转换、评分反例、冻结记录复核、桥接与新增手算 |

原训练数据及结果继续保留，本轮没有重复全部训练。单车测试 124 天：岭回归 MAE 859.81，MLP 三种子 1049.67／1118.79／958.56。数字测试 360 张：逻辑回归 95.56%，CNN 三种子 96.39%／96.39%／97.78%。模拟传感器测试 1620 个窗口：中值 MAE／RMSE 1.2997／1.6109 cm，CNN 1.2241／1.6239 cm。模拟分割测试 100 张：阈值 IoU 0.7252，Tiny U-Net IoU 0.8878、Dice 0.9405。虚构手册检索 15 问：Recall@1 0.9333，Recall@3 1.0，MRR 0.9667。数据、任务与协议分别见各章。

基础 Agent 三项目使用离线回复驱动真实工具执行。知识库完成搜索、读取和连续引文核验；订单清洗 13 行为 10 行，收入 1470.00、成本 913.00、利润 557.00；工单恢复等待状态并按模拟批准完成一次写入，同操作重放的事件总数保持 1。传感器桥接另停在待审阅状态，业务变更事件为 0。

## 真实模型实验

固定 LungSight 公开资料提交为 80932e2d34eefbfd3031e0a04370986562cf40ac。8 段资料与人工构造教学任务作为工具返回；不读取患者数据，不运行 CT 分类。请求与响应模型名均为 deepseek-flash，非思考模式、温度 0；每题最多 7 次模型调用、10 次工具调用。

| 执行组 | 运行数 | 指定自动检查通过 | 模型／工具次数 | 输入／输出 token | 耗时中位数（秒） | 参考美元 |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(group_rows)}

20 道冻结题的事实、数值和来源检查均通过。题目由作者围绕同一小型证据包编写，与开发题共享资料；此结果描述这些教学任务的契约检查。开放说明文字另外编辑复核。

综合初稿 REPORT01 的数值与引文检查通过，但把人工构造概率描述成实际推理输出。修订任务要求后，REPORT02 明确数据来源，并分别叙述公开架构参照与模拟待复核状态。两份输出与 semantic_review.json 均保留，原自动分数未改写。

全部 32 次任务合计 89 次模型请求、79 次工具调用，输入 120517、输出 9511 token。按核验日高峰缓存未命中输入价 0.30 美元／百万与输出价 1.20 美元／百万，参考估算约 0.0475683 美元；缓存和时段影响账户实扣。资料包没有账户账单。价格来源为 DeepSeek 官方价格表，核验日期 2026-11-10。

## 结果范围

模拟传感器、缺陷、手册、订单与工单用于教学；原训练实验与真实模型工具实验分别报告。Anthropic 适配器完成本地消息测试，远端实测采用 DeepSeek。MCP 实现是指定版本的最小协议子集。临床性能、多 Agent 对照和线上负载属于后续独立实验。
'''
(ROOT/'示例验证记录.md').write_text(record,encoding='utf-8')

doc=fitz.open(ROOT/'深度学习与AI_Agent开发_精排版.pdf')
ids=['copyright','overview','section-03-08','section-38-10','section-40-11','section-42-09','bibliography']
selected=[0,1]+[locations['locations'][id]['physical']-1 for id in ids]
labels=['原创封面','三位作者 · 28 pt','版权与作者信息','简明总目录','进阶阅读提示','真实模型实验','五折数值讲解','传感器贯穿演练','参考文献与资料']
canvas=Image.new('RGB',(1560,2370),'#edf2f3');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',34);small=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',23)
draw.text((38,24),'深度学习与 AI Agent 开发 · 修订版',font=font,fill='#183543')
draw.text((40,80),f'{pages} 页 / 44 章 / {figures} 组图示 / 8 个项目与综合案例',font=small,fill='#5c737c')
for i,(p,label) in enumerate(zip(selected,labels)):
    pix=doc[p].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((474,670),Image.Resampling.LANCZOS)
    x=40+i%3*510;y=156+i//3*738
    draw.text((x,y-32),label,font=small,fill='#315e7a');canvas.paste(im,(x,y))
canvas.save(ROOT/'教材排版预览.png')
doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(ROOT/'封面预览.png')
doc[1].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(ROOT/'作者扉页预览.png')
doc[locations['locations']['section-40-11']['physical']-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False).save(ROOT/'宋体正文预览.png')

main=['深度学习与AI_Agent开发_精排版.pdf','深度学习与AI_Agent开发_阅读版.html','深度学习与AI_Agent开发.md']
manifest={'title':'深度学习与 AI Agent 开发：原理、实战与应用','edition':today+' 修订版',
 'authors':author['authors'],'pages':pages,'front_pages':locations['front_pages'],'body_pages':locations['body_pages'],
 'copyright_pages':locations['copyright_pages'],'reference_pages':locations['reference_pages'],'references':76,
 'licenses':{'book_text_and_figures':'rights reserved','original_code':'MIT','scope':'publication/code_license_scope.json','third_party':'THIRD_PARTY_NOTICES.md','lungsight':'retains upstream rights; AGPLv3 reference only'},
 'chapters':44,'figures':figures,'base_projects':8,'real_model_case':'LungSight public snapshot and constructed tasks',
 'programming_intro_chapter':21,'author_signature_pt':28,'toc_entries':pdf['toc_entries'],'overview_entries':47,
 'checks':{'core':27,'mcp':8,'numerical':26,'final_project':final_projects['passed'],'final_content':final_content['total_checks']},
 'live_model':{'provider':'DeepSeek','model':'deepseek-flash','date':'2026-11-10','frozen_tasks':20,'specified_checks_passed':20,'runs_including_controls':32,'input_tokens':120517,'output_tokens':9511,'cost_estimate_usd':.0475683,'billing_receipt':False},
 'files':{p:{'bytes':(ROOT/p).stat().st_size,'sha256':sha(ROOT/p)} for p in main}}
(ROOT/'交付清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

root_names=main+['阅读指南.md','修订说明.md','示例验证记录.md','数据与引用说明.md','排版与编辑说明.md',
 '版权页.md','参考文献.md','作者与版本信息.md','LICENSE.md','LICENSE-CODE.txt','THIRD_PARTY_NOTICES.md',
 'build_publication.py','verify_publication.py','publication/references.json','publication/references.bib',
 'publication/reference_audit.json','publication/bib_validation.json','publication/rights_decision.json','publication/repository.json',
 'publication/code_license_scope.json','publication/publication_check.json','publication/licenses/DejaVu-LICENSE.txt',
 '近年AI应用案例来源.md','零基础补充记录.json','语气修订记录.json','版本清理记录.json','交付清单.json',
 '教材排版预览.png','封面预览.png','宋体正文预览.png','作者扉页预览.png','零基础增补预览.png',
 'author_page.json','author_page_check.json','author_revision_check.json','author_screen_check.json','author_screen_check.json',
 'assemble_revised.py','build_book.mjs','finish_layout.py','check_revised.py','finalize_revised.py','finalize_final.py',
 'prepare_fonts.py','prepare_style_fonts.py','prepare_author_fonts.py','create_cover_art.py','create_frontispiece.py',
 'verify_beginner_material.py','verify_beginner_layout.py','check_beginner_screen.mjs','add_beginner_material.py',
 'verify_final_projects.py','verify_final_book_content.py','revise_final.py','complete_final_case.py','polish_final_build.py','update_project_cli.py',
 'configure_deepseek.ps1','final_project_checks.json','final_content_check.json','final_revision_config.json','final_revision_log.json','final_visual_review.json',
 'book.css','package.json','requirements-projects.txt','requirements-book.txt',
 'source_check.json','layout_check.json','pdf_check.json','chapter_pages.json','page_locations.json','toc_entries.json','book_structure.json',
 'layout_annotations.json','validation_reference.json','content_preservation_check.json','beginner_check.json','beginner_layout_check.json',
 'numpy_mlp_demo.py','pytorch_mlp_demo.py','pytorch_mlp.pt','derivation_lab.py']
entries=[ROOT/name for name in dict.fromkeys(root_names)]
for folder in ['新版章节','figures','projects','agent_projects','case_study','experiment','vendor']:
    entries.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and not any(x in p.parts for x in ['__pycache__','_local','my_results']) and p.suffix not in ['.pyc','.tmp','.log'])
entries=sorted(set(entries))
write_code_scope(entries)
publication_check=verify_publication(check_scope=True)
assert publication_check['passed']
assert all(p.is_file() for p in entries)
leaks=[]
for p in entries:
    relative=p.relative_to(ROOT).as_posix()
    if '_local/' in relative or p.name.endswith('credential.xml'):leaks.append(relative)
    if p.suffix.lower() in {'.py','.js','.mjs','.ps1','.json','.md','.html','.txt','.csv','.yaml','.yml'}:
        if re.search(rb'sk-[A-Za-z0-9_-]{20,}',p.read_bytes()):leaks.append(relative)
assert not leaks,{'credential_pattern_files':leaks}
archive=ROOT/'深度学习与AI_Agent开发_完整资料.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in entries:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(name)).hexdigest()==manifest['files'][name]['sha256'] for name in main)
    scope=load('publication/code_license_scope.json')
    assert all(hashlib.sha256(z.read(e['path'])).hexdigest()==e['sha256'] for e in scope['files'])
    assert all(name in z.namelist() for name in ['LICENSE.md','LICENSE-CODE.txt','THIRD_PARTY_NOTICES.md','publication/references.bib','版权页.md','作者与版本信息.md'])
    count=len(z.namelist())
check={'archive_files':count,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'zip_crc_passed':True,
       'private_files_excluded':True,'credential_pattern_matches':0,'main_file_hashes_match':True,'pages':pages,'figures':figures,
       'references':76,'mit_scope_files':len(scope['files']),'mit_scope_hashes_match':True,'publication_materials_included':True}
(ROOT/'final_delivery_check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(check,ensure_ascii=False))
