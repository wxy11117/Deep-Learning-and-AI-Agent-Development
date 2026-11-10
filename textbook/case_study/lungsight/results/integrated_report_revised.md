# LungSight 综合教学报告：修订后的来源表达

本例概率由作者人工构造、按 LungSight 接口组织（A/B/C/D 为抽象教学类别），非真实患者推理结果。五折平均概率最高为 B 类，均值 0.51；五折中 4 折的折内最高类别为 B、1 折为 C，一致比例 0.8，说明存在一定折间分歧（B 类折间极差 0.35）。该任务复核状态为 pending，属模拟待复核。公开仓库参照信息：LungSight 为肺部 CT 四分类科研教学原型，非医疗器械；其本地五折 ResNet18 研究推理权重版本为 research-fivefold-20260902-165455，与本任务 model_version 一致。

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

## 资料出处

- [LS01 · 本地模型架构 五折 ResNet18 权重版本](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L9-L9)：当前版本已经把网页中的模拟结果替换为真实的本地五折 ResNet18 研究推理，并完成任务留痕、复核和报告下载闭环。
- [LS01 · 本地模型架构 五折 ResNet18 权重版本](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L9-L9)：运行权重是审计后重新训练的 `research-fivefold-20260902-165455`，不是最初程序包权重。
- [LS02 · 项目定义 四分类 科研教学用途](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L5-L5)：LungSight 是面向肺部 CT 四分类研究的本地智能辅助分析原型，包含影像任务、五折模型推理、质控提示、医生复核、循证医学问答和结构化报告工作流。
- [LS02 · 项目定义 四分类 科研教学用途](https://github.com/wxy11117/LungSight/blob/80932e2d34eefbfd3031e0a04370986562cf40ac/README.md#L5-L5)：当前版本仅供科研、教学与产品验证，不是医疗器械，不能替代医生诊断、病理检查或治疗决策。
