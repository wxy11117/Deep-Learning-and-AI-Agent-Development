# 五个模型与检索项目的运行索引

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
