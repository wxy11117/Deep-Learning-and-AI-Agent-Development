# LungSight：真实模型工具循环的教学案例

配套教材第 38.10—38.11、40.10—40.14 节。固定公开项目资料，加上作者构造的 A/B/C/D 五折概率，解释深度模型接口、确定性计算与 Agent 工具调用如何连接。此目录是教材扩展；上游 LungSight 的固定检索生成流程与本例的模型工具循环分别说明。

本次使用仓库 `wxy11117/LungSight`，提交 `80932e2d34eefbfd3031e0a04370986562cf40ac`。源文件位置、SHA-256、原文行号与链接见 `source_manifest.json` 和 `documents.json`。教学任务没有患者数据，未执行 CT 推理，也不操作上游系统。

## 先读保存的结果

- `results/evaluation/`：20 道冻结教学题的完整运行。12 道资料查找、5 道数值、2 道信息缺失、1 道版本冲突，指定检查均通过。
- `results/repeat/`：L06、L14、L19 各追加两次运行，6 次指定检查通过。
- `results/fault_before/`、`fault_after/`：首次搜索注入超时，处理前中断，转换为结构化错误后模型重试并完成。
- `results/integrated/`、`integrated_revised/`：综合报告 REPORT01、REPORT02；前者数值检查通过但文字混淆数据来源，后者增加来源要求后重新生成。
- `results/semantic_review.json`：编辑核对记录，保留来源表述问题和修订依据。
- `results/integrated_report_revised.md`：修订报告阅读稿。
- `results/summary.json`：按执行组汇总 token、调用、耗时与费用参考。

20 道题由作者围绕同一小型证据包编写，与 2 道开发题共享资料。通过数对应任务规定的事实、数值和来源检查；开放文字另做编辑复核。原始输出和自动评分均保留，便于读者检查评分器覆盖了什么。

## 重新运行

Python 3.11 或 3.12，标准库即可。先在本机配置 `DEEPSEEK_API_KEY`，可选 `DEEPSEEK_MODEL`。默认模型 `deepseek-flash`，官方地址 `https://api.deepseek.com/chat/completions`，非思考模式、温度 0，最多 7 次模型调用与 10 次工具调用。密钥不写入程序、实验记录或教材。根目录的 `configure_deepseek.ps1` 可在 Windows 本机以密码输入框配置加密凭据；该凭据仅供当前 Windows 用户读取，私有文件不随包分发。

在教材根目录依次执行：

```powershell
python case_study/lungsight/run_experiment.py --phase development --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_experiment.py --phase evaluation --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_experiment.py --phase repeat --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_experiment.py --phase fault --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_integrated.py --live --output-dir case_study/lungsight/my_results
python case_study/lungsight/run_revised_report.py --live --output-dir case_study/lungsight/my_results
```

`--live` 显式发起计费请求。先检查开发题连接正常再继续。每个输出目录保留已有题目用于恢复，重新做一轮应使用新目录；原随书 `results` 不覆盖。修改问题、提示或资料后，创建新实验目录并记录差异。

仅汇总已有文件，不请求服务：

```powershell
python case_study/lungsight/run_experiment.py --phase summary
python verify_final_projects.py
```

`verify_final_projects.py` 还会运行本地模型项目检查，需要安装根目录 requirements-projects.txt 中的依赖，并会更新对应离线结果；它不发送模型请求。若只想阅读结果，打开 JSON 和 Markdown 即可。

## 指标与复核

2026-11-10 的记录共 32 次任务运行、89 次模型请求、79 次工具调用。20 道冻结题耗时中位数 3.303 秒；三道选定题的额外 6 次运行中位数 3.751 秒。端到端计时包含网络等待、工具执行和验收。

实际响应累计输入 120517、输出 9511 token。按当日高峰缓存未命中输入价 0.30 美元／百万、输出价 1.20 美元／百万，参考费用约 0.0475683 美元。该参考将所有输入按缓存未命中计算；缓存和时段影响实际账单。价格来源：[DeepSeek 官方价格表](https://api-docs.deepseek.com/quick_start/pricing/)，核验日期 2026-11-10。

记录中的 `requested_model`、`returned_models` 保留接口实际名称；服务别名不是不可变的模型权重哈希。`implementation_sha256` 指向运行时各文件的内容；`execution_sources` 保留运行包装脚本调整前的对应源码，按哈希命名，便于核对记录。`case_tools.py`、核心运行时、适配器保持对应实验实现。

教学任务中的平均概率来自显式矩阵，程序复算后返回模型。综合报告还要审查数据来源、对象和状态：结构化数值正确与整段说明准确，是两个分别核对的条件。
