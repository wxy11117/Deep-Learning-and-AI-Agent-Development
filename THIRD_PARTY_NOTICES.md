# 第三方资料与许可说明

本表对应 2026 年 11 月修订版，核对日期为 2026-11-11。教材原创代码的 MIT 授权范围见 `LICENSE.md`，下列内容保持原来源和原许可。

| 内容 | 来源与许可 | 本版分发方式 |
|---|---|---|
| Noto Serif SC、Noto Sans SC 字体子集 | Noto 项目；SIL Open Font License 1.1；许可见 [textbook/vendor/fonts/LICENSE.txt](textbook/vendor/fonts/LICENSE.txt) | 随包保留开放字体子集、来源和许可；用于 HTML 与 PDF 排版。 |
| Great Vibes | Google Fonts；SIL Open Font License 1.1；许可见 [textbook/vendor/fonts/GreatVibes-OFL.txt](textbook/vendor/fonts/GreatVibes-OFL.txt) | 原字体随包提供，作者署名使用其字形。 |
| Windows 系统字体 | SimSun、KaiTi 及排版中使用的其他系统字体；适用其原有使用与文档嵌入条款 | 从合法安装的系统环境读取并嵌入文档所需字形；资料包不提供这些字体的独立字体文件。 |
| DejaVu 字体 | Matplotlib 随附的 DejaVu 字体；Bitstream Vera / DejaVu 许可见 [textbook/publication/licenses/DejaVu-LICENSE.txt](textbook/publication/licenses/DejaVu-LICENSE.txt) | 部分科学图示的西文与数学字形使用该字体，保留许可说明。 |
| KaTeX | KaTeX 项目；MIT；许可见 [textbook/vendor/katex/LICENSE](textbook/vendor/katex/LICENSE) | 保存公式渲染资源与字体，保留原版权声明。 |
| Mermaid | Mermaid 项目；MIT；许可见 [textbook/vendor/mermaid/LICENSE](textbook/vendor/mermaid/LICENSE) | 保存结构图生成依赖与许可。 |
| Bike Sharing 数据集 | Hadi Fanaee-T；UCI；CC BY 4.0；DOI：10.24432/C5W894 | 保存原始数据压缩包与实验结果；原始数据未改动，滞后特征和划分由本书实验程序生成。 |
| Optical Recognition of Handwritten Digits | E. Alpaydin、C. Kaynak；UCI；CC BY 4.0；DOI：10.24432/C50P49 | 本书使用 scikit-learn 的 `load_digits` 子集并重新划分；数据源与改动说明见数据说明及第 23 章。 |
| LungSight 仓库快照与资料摘录 | wxy11117/LungSight；提交 `80932e2d34eefbfd3031e0a04370986562cf40ac` | 保留来源路径、行号、哈希与原文件。该提交未发现独立许可文件，未纳入本书代码 MIT 授权。 |
| 丘吉尔题辞 | International Churchill Society 保存的 1942-11-10 演讲 The Bright Gleam of Victory | 采用据原文自译的短句，标明演讲者、日期和来源；来源见参考文献 [76]。 |
| 论文、官方文档与产品案例资料 | 各原作者与发布机构 | 本书提供引用与教学分析；文献元数据和链接集中在卷末。参考文献表不构成对原文、模型或第三方软件的再授权。 |

训练及构建依赖由读者在自己的环境安装，本资料包不复制本机 Python 或 Node 的完整依赖目录。各依赖适用其原许可。

CC BY 4.0 要求保留适当署名、许可链接并说明修改；本书的数据署名和改动说明见上表与 [数据与引用说明](textbook/数据与引用说明.md)。许可原文：[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)。

系统字体的文档嵌入与独立字体文件分发是不同的使用方式，核对依据见 [Microsoft Font redistribution FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)。

参考入口：[Noto CJK](https://github.com/notofonts/noto-cjk)、[Great Vibes](https://github.com/google/fonts/tree/main/ofl/greatvibes)、[UCI Bike Sharing](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset)、[UCI Optical Recognition of Handwritten Digits](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits)、[LungSight 固定提交](https://github.com/wxy11117/LungSight/tree/80932e2d34eefbfd3031e0a04370986562cf40ac)。
