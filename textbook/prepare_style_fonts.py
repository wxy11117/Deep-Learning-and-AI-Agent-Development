"""Subset open-source heading fonts; keep the reader's Song-style body font."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'_build_deps'))
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
text=(ROOT/'深度学习与AI_Agent开发.md').read_text(encoding='utf-8')
text+='第一二三四五六七八九十篇章目录前言阅读约定例题算例解析解答注记反例思考实战资料原理应用'
cover='最终简明深度学习与开发原理实战应用从神经网络到智能体系统数学模型训练表示工具状态证据项目附源代码图示推导实践排版修订年月'
for weight,chars in [(700,text),(900,cover)]:
    f=TTFont(r'C:\Windows\Fonts\NotoSansSC-VF.ttf')
    f=instantiateVariableFont(f,{'wght':weight},inplace=True)
    family=f'BookSans{weight}'
    for record in f['name'].names:
        if record.nameID in (1,4,6,16):record.string=family.encode(record.getEncoding())
        elif record.nameID in (2,17):record.string='Regular'.encode(record.getEncoding())
    options=subset.Options();options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
    s=subset.Subsetter(options=options);s.populate(text=chars+''.join(chr(i) for i in range(32,127)))
    s.subset(f);f.save(ROOT/f'vendor/fonts/BookSans-{weight}.ttf')
    print('Prepared heading weight',weight)
