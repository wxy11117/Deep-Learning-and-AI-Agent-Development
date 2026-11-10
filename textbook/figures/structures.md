# 教材结构图源文件

以下 Mermaid 图是关系图的可编辑源文件。图像由 render_structures.mjs 导出；数值曲线由独立 Python 脚本生成。

<!-- FIG:diagram_map -->
~~~mermaid
flowchart TB
    accTitle: AI And Learning Map
    accDescr: 人工智能包含机器学习等方法，深度学习通过多层变换学习表示；应用任务与方法结构是不同维度。
    ai["人工智能<br/>感知、推理、规划与行动"] --> ml["机器学习<br/>从数据或交互中改进"]
    ai --> symbolic["规则、搜索与符号方法"]
    ml --> classic["线性模型、树、核方法"]
    ml --> representation["表示学习<br/>学习有用的特征"]
    representation --> deep["深度学习<br/>多层可学习变换"]
    deep --> architectures["CNN · RNN · Transformer"]
    architectures --> tasks["分类 · 回归 · 分割 · 生成"]
    classDef main fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef info fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    class ai,ml,representation,deep main
    class symbolic,classic,architectures,tasks info
~~~

<!-- FIG:diagram_train -->
~~~mermaid
flowchart LR
    accTitle: Training And Model Selection
    accDescr: 训练数据产生损失与梯度以更新参数，验证集用于选择检查点，冻结后的模型才进入测试评估。
    batch["训练<br/>批次"] --> forward["前向<br/>计算"]
    forward --> loss["损失"]
    loss --> backward["反向<br/>传播"]
    backward --> update["优化器<br/>更新参数"]
    update --> forward
    update --> validation["验证集<br/>评估"]
    validation --> select["保存最佳<br/>检查点"]
    select --> frozen["冻结方案<br/>测试并报告"]
    classDef main fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef checked fill:#dcfce7,stroke:#16a34a,color:#14532d
    class batch,forward,loss,backward,update main
    class validation,select,frozen checked
~~~

<!-- FIG:diagram_branch -->
~~~mermaid
flowchart LR
    accTitle: Branching Computational Graph
    accDescr: a等于wx，损失为a平方加三倍a。反向传播在共享节点a累加两条路径的梯度。
    input["x = 2<br/>w = 1"] --> a["a = wx<br/>a = 2"]
    a --> square["u = a²<br/>u = 4"]
    a --> linear["v = 3a<br/>v = 6"]
    square --> total["L = u + v<br/>L = 10"]
    linear --> total
    total -. "汇总梯度" .-> grad["∂L/∂a<br/>4 + 3 = 7"]
    grad -. "乘 x" .-> result["∂L/∂w<br/>7 × 2 = 14"]
    classDef value fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef gradient fill:#fef9c3,stroke:#ca8a04,color:#713f12
    class input,a,square,linear,total value
    class grad,result gradient
~~~

<!-- FIG:diagram_split -->
~~~mermaid
flowchart LR
    accTitle: Data Split Before Fitting
    accDescr: 原始数据先按独立单位划分，预处理仅在训练集拟合，同一变换应用到验证与测试。
    raw["原始数据<br/>分组与时间"] --> split["先划分"]
    split --> train["训练集"]
    split --> valid["验证集"]
    split --> test["测试集"]
    train --> fit["只在训练集<br/>拟合"]
    fit --> select["验证集<br/>选择超参数"]
    valid --> select
    select --> final["冻结变换<br/>与模型"]
    final --> evaluate["最终<br/>测试"]
    test --> evaluate
    classDef main fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef held fill:#dcfce7,stroke:#16a34a,color:#14532d
    class raw,split,train,fit,select,valid main
    class test,final,evaluate held
~~~

<!-- FIG:diagram_transformer -->
~~~mermaid
flowchart LR
    accTitle: Pre Normalized Transformer Block
    accDescr: 一个Pre-LN Transformer块先归一化再做注意力与前馈变换，两条残差路径保留输入信息。
    input["输入 X"] --> attn["LayerNorm<br/>↓<br/>多头自注意力"]
    attn --> add_one["残差相加<br/>得到 U"]
    input --> add_one
    add_one --> ffn["LayerNorm<br/>↓<br/>逐位置前馈网络"]
    ffn --> add_two["残差相加<br/>得到 V"]
    add_one --> add_two
    classDef main fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef sum fill:#fef9c3,stroke:#ca8a04,color:#713f12
    class input,attn,ffn main
    class add_one,add_two sum
~~~

<!-- FIG:diagram_unet -->
~~~mermaid
flowchart LR
    accTitle: Tiny UNet Feature Shapes
    accDescr: 高分辨率特征通过跳跃拼接送到解码器，与上采样后的低分辨率特征共同产生像素logits。
    enc["输入与编码<br/>1→8→8 通道<br/>32×32"]
    enc --> down["池化与卷积<br/>16×16×16"]
    down --> up["双线性上采样<br/>16×32×32"]
    up --> concat["沿通道拼接<br/>24×32×32"]
    enc --> concat
    concat --> decode["卷积解码<br/>24→8→1 通道<br/>32×32 logits"]
    classDef main fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef merge fill:#dcfce7,stroke:#16a34a,color:#14532d
    class enc,down,up,decode main
    class concat merge
~~~

<!-- FIG:diagram_rag -->
~~~mermaid
flowchart LR
    accTitle: Retrieval Augmented Answer Pipeline
    accDescr: 文档经解析和索引后参与检索，候选资料经过重排序供生成使用，最后检查回答证据和引用。
    docs["版本化<br/>文档"] --> index["解析、切块<br/>建立索引"]
    query["用户<br/>问题"] --> search["检索候选"]
    index --> search
    search --> rank["重排序<br/>保留证据"]
    rank --> generation["生成<br/>回答"]
    query --> generation
    generation --> verify["核对主张<br/>与引用"]
    verify --> answer["回答或说明<br/>资料不足"]
    classDef done fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef design fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    class docs,index,query,search done
    class rank,generation,verify,answer design
~~~

<!-- FIG:diagram_diffusion -->
~~~mermaid
flowchart LR
    accTitle: Diffusion Training And Sampling
    accDescr: 训练时从真实样本和已知噪声构造监督信号；生成时从噪声开始重复调用学习到的去噪模型。
    real["真实样本 x₀"] --> noisy["抽取 t 与噪声<br/>构造 xₜ"]
    noisy --> predict["网络预测噪声"]
    predict --> loss["与已知噪声<br/>计算训练损失"]
    noise["生成起点<br/>随机噪声 xT"] --> denoise["去噪模型<br/>与采样更新规则"]
    denoise --> previous["较低噪声状态"]
    previous --> denoise
    previous --> sample["最终样本"]
    classDef training fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef sampling fill:#dcfce7,stroke:#16a34a,color:#14532d
    class real,noisy,predict,loss training
    class noise,denoise,previous,sample sampling
~~~

