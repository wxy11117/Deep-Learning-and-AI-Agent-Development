# 三个 Agent 教学项目

配套《深度学习与 AI Agent 开发：原理、实战与应用》第 32—43 章。默认使用固定的模型回复回放，实际执行本地工具、引文核验、数据聚合、SQLite 事务与检查点恢复。默认运行不需要密钥，也不调用模型服务。

## 从这里运行

在教材根目录、Python 3.12 环境中执行：

```powershell
python agent_projects/run_projects.py
python agent_projects/test_projects.py
python agent_projects/test_mcp.py
```

以上三个命令只使用 Python 标准库。默认运行覆盖六条虚构设备说明、十三行模拟订单，以及临时数据库中的一张模拟工单。结果写入 `agent_projects/results`。再次执行会更新同名结果；工单数据库位于临时目录，检查完毕后自动清理。

若要重新生成订单图表，先安装 `requirements-book.txt` 中的绘图依赖，再运行：

```powershell
python agent_projects/plot_report.py
```

图表提供 PNG、PDF、SVG；Markdown 报告引用同目录的 PNG。

## 项目与源码

| 内容 | 文件 | 结果证据 |
|---|---|---|
| 有界工具循环、参数检查、轨迹 | core.py | 三份 trace.json；工程测试 |
| 带版本与原文引用的知识库 | knowledge.py | knowledge_trace.json |
| 订单检查、清洗与 Decimal 聚合 | analysis_tools.py | orders_report.md、orders_chart.* |
| 提案、批准、事务、幂等和恢复 | workflow.py | offline_results.json 的 workflow 字段 |
| 显式可选的真实模型适配器 | live_provider.py | 本版只执行本地消息夹具测试 |
| 最小 stdio MCP 服务 | mcp_server.py | mcp_verification.json |

固定模型回复是可复现的测试输入，检查工具与运行时路径；真实模型选择工具的实验见下方 DeepSeek 综合案例。27 项工程检查与 8 项 MCP 集成检查的含义、覆盖范围和局限见教材第 38 章及根目录的验证记录。

## MCP 实验

`test_mcp.py` 会真正启动服务子进程并通过标准输入输出交换 JSON-RPC 消息，无需安装 MCP SDK。手动运行服务的命令是：

```powershell
python agent_projects/mcp_server.py
```

服务启动后等待客户端逐行发送消息；它不是交互问答终端。实现固定为协议 2025-11-25 的最小教学子集，包括初始化、通知、ping、tools/list、tools/call，以及两个只读手册工具。没有实现远程传输、授权、分页或取消，不构成完整协议一致性声明。

## 可选真实模型接入

适配器使用 Anthropic Messages API。需要读者在自己的终端环境中设置 `ANTHROPIC_API_KEY` 与 `ANTHROPIC_MODEL`，选择账户实际可用的模型；不要把密钥写进源代码或资料包。随后显式执行：

```powershell
python agent_projects/run_projects.py --live
```

这会产生账户费用，并将对应的虚构说明或模拟订单结果发送给模型服务。真实运行轨迹保存为带 `live` 的文件，默认离线轨迹保留；订单报告和图表仍写入同名输出文件。工单环节依然只操作临时模拟数据库，其批准来自测试夹具，不能接到真实业务后直接当作人工批准。

本节 Anthropic 适配器完成了本地消息测试；远端实测使用另一份 DeepSeek 适配器。当前代码显式使用 API 版本 `2023-06-01`，重新接入时应核对服务方文档、消息类型和结束原因。真实模型可能产生不满足任务契约的结果；程序会报错，而不会在模型结束后替它补造成功轨迹。

## 修改项目时的建议

先修改一个工具或一个判分条件，再运行相应检查。例如把订单的重复编号改成冲突金额，应得到明确拒绝；把手册引用中的一个字改错，应在原文核验时失败；修改工单版本后再使用旧提案，应触发版本冲突。之后另建任务集评价真实模型，并报告失败案例与成本。

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
