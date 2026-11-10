"""Assemble the revised textbook; chapter files are the canonical edited source."""
from pathlib import Path
import re,json,subprocess,sys
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'build_publication.py')],check=True)
chapters=[]
for i in range(1,45):
    s=(ROOT/f'新版章节/{i:02}.md').read_text(encoding='utf-8').strip()
    assert f'<a id="chapter-{i:02}"></a>' in s
    assert re.search(rf'^## 第 {i} 章',s,re.M)
    chapters.append(s)
body='\n\n---\n\n'.join(chapters)
titles=re.findall(r'^## 第 (\d+) 章　(.+)$',body,re.M)
toc='\n'.join(f'{n}. [{title}](#chapter-{int(n):02})' for n,title in titles)
front='''# 深度学习与 AI Agent 开发：原理、实战与应用

从神经网络、大语言模型到可验证的智能体系统

2026 年 11 月修订版

## 阅读说明

这本书把两类问题连在一起：模型为什么能从数据中学习，以及怎样把模型放进能够完成任务的应用。前者需要数学、实验与对泛化的理解，后者需要工具、状态、证据与工程边界。两条线最终在实际项目中相遇。

第一篇为第 1—28 章，依次建立机器学习地图、数学与训练基础、主要架构和四个预测或视觉项目；第二篇为第 29—31 章，连接大语言模型训练、迷你 Transformer 代码和文档检索；第三篇为第 32—44 章，系统讲解 Agent 接口、工具循环、检索与记忆、持久化、MCP、评估部署，以及三个完整工程项目和综合练习。

首次阅读先掌握输入与标签、张量形状、一次梯度更新、训练与测试划分，再向网络架构推进。第 3.8、4.6—4.7、7.8 节中的分解、曲率和雅可比标为进阶选读；第一遍先抓住它们解决的问题，学习压缩、优化或多分类时再回读推导。编程入门与环境准备保留在第 21 章，八个项目的开头集中给出单独运行入口、输出位置与核对步骤。

希望先做 Agent 的读者，可从第 29、31、32—34 章进入，再选择第 40—42 章的项目，遇到表示、概率与训练概念时回查前篇。第 42.9 节将传感器估计、异常规则、手册与工单串起来；第 38、40 章的 LungSight 综合案例连接模型结果、公开项目资料和真实大模型工具调用。

共享单车和手写数字项目使用公开数据，传感器与分割项目使用模拟数据，检索和 Agent 手册为教学虚构内容。八个基础项目附有实际运行记录：前五个记录模型训练或检索结果，三个 Agent 项目用固定回复驱动本地工具、数据库与协议测试。新增 LungSight 案例使用固定版本的公开资料和明确标注的构造概率，通过 DeepSeek 实际完成工具选择；冻结题、重复运行与故障注入分别保存。实验条件、结果和费用估算集中见第 38.10—38.11 节。

零基础读者可以先跟着苹果计价、成绩表和查手册等小例子理解问题，再把数字换成符号，接着阅读推导与代码。抽象难点配有手算和图解，近年应用穿插介绍原理怎样进入真实系统。遇到陌生术语可回查第 44 章；每次读懂一个公式与程序动作的对应关系，比一次记住全部符号更有帮助。

正文采用小四号宋体，章与节标题使用粗黑体，注记使用楷体，数学和代码分别使用专用公式字体与等宽字体。蓝、青绿、紫、莓红和暖橙用于章节导航与图示；标题、编号和标签共同标明内容层次。配套源稿、图形源文件、程序、实际结果与验证说明随完整资料包提供。

## 目录

'''
author=json.loads((ROOT/'author_page.json').read_text(encoding='utf-8'))
author_source='## 作者扉页\n\n![从表示学习到 Agent 行动的原创图示]('+author['artwork']+')\n\n作者：'+author['author']+'\n\n> '+''.join(author['quote'])+'\n\n—— '+author['attribution']+'\n\n['+author['source_note']+']('+author['source_url']+')\n\n'
front=front.replace('## 阅读说明\n',author_source+(ROOT/'版权页.md').read_text(encoding='utf-8')+'\n\n## 阅读说明\n')
backmatter='\n\n<a id="book-references"></a>\n\n'+(ROOT/'参考文献.md').read_text(encoding='utf-8')
(ROOT/'深度学习与AI_Agent开发.md').write_text(front+toc+'\n\n---\n\n'+body+backmatter+'\n',encoding='utf-8')
paragraphs=[p for p in body.split('\n\n') if p and not p.startswith(('#','<','|','$$','~~~','```','- ')) and '\n' not in p]
lengths=sorted(len(re.findall(r'[\u4e00-\u9fff]',p)) for p in paragraphs)
stats={'chapters':len(titles),'source_chars':len(body),'cjk_chars':len(re.findall(r'[\u4e00-\u9fff]',body)),
       'prose_paragraphs':len(lengths),'paragraph_cjk_percentiles':{str(q):lengths[round((len(lengths)-1)*q)] for q in [0,.1,.25,.5,.75,.9,1]}}
(ROOT/'source_check.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False))
