# Agent 篇结构图源文件

所有图为结构示意；模型表现需另行评测。原图与正文一一对应。

<!-- FIG:diagram_agent_loop -->
~~~mermaid
flowchart LR
 accTitle: Agent 的行动观察循环
 accDescr: 模型建议动作，经运行时校验后执行，观察更新上下文，满足条件才结束。
 context[上下文与状态] --> model[模型建议]
 model --> gate{验证请求}
 gate -->|合法| tool[执行工具]
 tool --> observation[实际结果]
 observation --> context
 gate -->|不合法| context
 model -->|满足结束条件| finish([验收结果])
 classDef input fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef control fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef check fill:#fef9c3,stroke:#ca8a04,color:#713f12
 classDef done fill:#dcfce7,stroke:#16a34a,color:#14532d
 class context,observation input
 class model,tool control
 class gate check
 class finish done
~~~

<!-- FIG:diagram_tool_sequence -->
~~~mermaid
sequenceDiagram
 accTitle: 模型与工具的调用时序
 accDescr: 运行时转发模型提出的工具请求，并将执行结果按调用编号送回模型。
 participant app as 应用
 participant model as 模型
 participant runtime as 执行器
 participant search as 检索工具
 app->>model: 问题与工具定义
 model-->>app: tool_use：编号 k1
 app->>runtime: 请求 k1 与参数
 runtime->>runtime: 名称、类型、范围检查
 runtime->>search: 合法查询
 search-->>runtime: 候选与版本
 runtime-->>app: 实际结果 k1
 app->>model: tool_result：编号 k1
 model-->>app: 继续读取或结束
~~~

<!-- FIG:diagram_evidence_pipeline -->
~~~mermaid
flowchart LR
 accTitle: 从资料到引用的证据链
 accDescr: 文档先按结构切块并保留版本，经过索引过滤、检索与读取形成可核对的引用。
 source[原文与版本] --> chunk[带来源的切块]
 chunk --> index[索引与权限过滤]
 index --> retrieve[检索候选]
 retrieve --> read[读取原文]
 read --> answer[回答与引用]
 classDef data fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef processing fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef output fill:#dcfce7,stroke:#16a34a,color:#14532d
 class source,chunk data
 class index,retrieve,read processing
 class answer output
~~~

<!-- FIG:diagram_workflow_state -->
~~~mermaid
stateDiagram-v2
 accTitle: 工单任务的状态转移
 accDescr: 从读取和提案进入等待审批，批准后执行，拒绝或取消进入终止状态。
 direction LR
 [*] --> inspecting
 state "读取与检查" as inspecting
 state "等待审批" as awaiting
 state "执行提案" as applying
 state "完成验收" as completed
 state "取消或拒绝" as cancelled
 state "失败待处理" as failed
 inspecting --> awaiting: 具体提案
 awaiting --> applying: 有效批准
 awaiting --> cancelled: 拒绝或取消
 applying --> completed: 结果核验
 applying --> failed: 执行失败
 completed --> [*]
 cancelled --> [*]
~~~

<!-- FIG:diagram_mcp_architecture -->
~~~mermaid
flowchart TB
 accTitle: MCP 宿主客户端服务端
 accDescr: 宿主内部维护模型交互和工具客户端，客户端连接不同服务端，业务权限分别验证。
 user[用户任务] --> host[AI 应用宿主]
 host <--> model[模型服务]
 host --> client_docs[文档客户端]
 host --> client_work[业务客户端]
 client_docs <--> server_docs[文档服务端]
 client_work <--> server_work[工单服务端]
 classDef entry fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef hostcolor fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef service fill:#dcfce7,stroke:#16a34a,color:#14532d
 class user,model entry
 class host,client_docs,client_work hostcolor
 class server_docs,server_work service
~~~

<!-- FIG:diagram_eval_loop -->
~~~mermaid
flowchart LR
 accTitle: Agent 评估与改进闭环
 accDescr: 固定任务在指定版本运行，收集轨迹并核验业务结果，在开发集修正问题，保留集保持独立。
 cases[冻结任务与环境] --> run[执行并保存轨迹]
 run --> grade[业务结果核验]
 grade --> classify[错误分类]
 classify --> dev[开发集改进]
 dev -.新版本回归.-> run
 classDef data fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef task fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef check fill:#fef9c3,stroke:#ca8a04,color:#713f12
 class cases data
 class run,dev task
 class grade,classify check
~~~

<!-- FIG:diagram_agent_deployment -->
~~~mermaid
flowchart TB
 accTitle: 可恢复任务的部署组成
 accDescr: 入口负责身份和任务接收，队列分配工作，执行器连接模型与工具，并把状态和事件写入存储。
 entry[入口与身份检查] --> queue[任务队列]
 queue --> worker[执行器]
 worker <--> model[模型服务]
 worker <--> tools[受限业务工具]
 worker --> state[持久状态]
 worker --> trace[事件与指标]
 classDef input fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef execution fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef storage fill:#dcfce7,stroke:#16a34a,color:#14532d
 class entry,queue input
 class worker,model,tools execution
 class state,trace storage
~~~

<!-- FIG:diagram_knowledge_agent -->
~~~mermaid
flowchart LR
 accTitle: 知识库项目的证据链
 accDescr: 搜索返回候选，读取形成实际证据，最终答案通过来源与引文检查，证据不足则弃答。
 query[问题与版本] --> search[搜索候选]
 search --> read[读取原文]
 read --> draft[生成回答]
 draft --> check{引用核验}
 check -->|通过| final[可追溯答案]
 check -->|证据不足| abstain[说明不足]
 classDef input fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef process fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef gate fill:#fef9c3,stroke:#ca8a04,color:#713f12
 classDef output fill:#dcfce7,stroke:#16a34a,color:#14532d
 class query,read input
 class search,draft process
 class check gate
 class final,abstain output
~~~

<!-- FIG:diagram_analysis_agent -->
~~~mermaid
flowchart TB
 accTitle: 数据分析的计算与表达
 accDescr: 原始数据先按口径检查清洗，再聚合为统一数值表，图表与报告共用数值，模型负责选择任务和解释。
 request[用户分析目标] --> choose[模型选择合法参数]
 choose --> inspect[检查与清洗工具]
 data[登记的 CSV 数据] --> inspect
 inspect --> aggregate[确定性聚合]
 aggregate --> table[统一数值表]
 table --> chart[图表]
 table --> report[报告与核对]
 classDef input fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef compute fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef output fill:#dcfce7,stroke:#16a34a,color:#14532d
 class request,data input
 class choose,inspect,aggregate compute
 class table,chart,report output
~~~

<!-- FIG:diagram_workorder_transaction -->
~~~mermaid
flowchart LR
 accTitle: 本地工单变更事务
 accDescr: 提案进入事务后先检查批准和版本，再改变业务状态并记录操作，发生异常则整体回滚。
 proposal[提案与操作编号] --> check[核对批准和版本]
 check --> update[条件更新工单]
 update --> event[消耗批准并记事件]
 event --> commit[提交事务]
 update -.异常.-> rollback[整体回滚]
 event -.异常.-> rollback
 classDef input fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef transaction fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef done fill:#dcfce7,stroke:#16a34a,color:#14532d
 classDef failure fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
 class proposal input
 class check,update,event transaction
 class commit done
 class rollback failure
~~~

<!-- FIG:diagram_multi_agent -->
~~~mermaid
flowchart TB
 accTitle: 具有独立验收的分工
 accDescr: 协调者将检索与分析分开，各自返回结构化结果，汇总之后仍由独立规则和证据核验。
 goal[任务契约] --> coordinator[协调者]
 coordinator --> retrieval[检索工作者]
 coordinator --> analysis[分析工作者]
 retrieval --> evidence[证据与未解问题]
 analysis --> numbers[数值与数据口径]
 evidence --> merge[汇总]
 numbers --> merge
 merge --> verify[独立业务验收]
 classDef input fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
 classDef agents fill:#ede9fe,stroke:#7c3aed,color:#3b0764
 classDef result fill:#dcfce7,stroke:#16a34a,color:#14532d
 classDef check fill:#fef9c3,stroke:#ca8a04,color:#713f12
 class goal input
 class coordinator,retrieval,analysis agents
 class evidence,numbers,merge result
 class verify check
~~~
