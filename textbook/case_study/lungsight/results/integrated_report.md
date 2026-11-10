# LungSight 教学任务科研结果说明草稿

数据：人工构造的 A/B/C/D 五折概率；公开仓库资料按固定提交保存。
生成方式：DeepSeek 实际选择并调用教材只读工具。

教学任务 DEMO-001 使用本地五折 ResNet18 研究推理，任务模型版本 research-fivefold-20260902-165455 与文档记载的审计后重训权重标识一致。五折平均概率中 B 类最高，为 0.51（A 0.11、C 0.28、D 0.10），故最高平均概率类别为 B。五折中四折的折内最高类别为 B、一折为 C，一致比例 0.8，说明存在一定折间分歧（B 与 C 的类别跨度均为 0.35，前两名差距 0.23）。当前复核状态为 pending，即尚未完成医生复核。以上为人工构造的教学数值，不构成临床结论。

## 结构化结果

```json
{
  "architecture": "ResNet18",
  "top_class": "B",
  "mean_probability": 0.51,
  "fold_agreement": 0.8,
  "review_status": "pending"
}
```

## 引用

- [LS01 · 本地模型架构 五折 ResNet18 权重版本](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L9-L9)：当前版本已经把网页中的模拟结果替换为真实的本地五折 ResNet18 研究推理
- [LS01 · 本地模型架构 五折 ResNet18 权重版本](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L9-L9)：运行权重是审计后重新训练的 `research-fivefold-20260902-165455`，不是最初程序包权重
- [LS02 · 项目定义 四分类 科研教学用途](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L5-L5)：当前版本仅供科研、教学与产品验证，不是医疗器械，不能替代医生诊断、病理检查或治疗决策。
