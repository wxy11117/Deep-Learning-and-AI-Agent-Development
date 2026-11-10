"""Prepare a compact, medium-weight Song-style title font for the author page."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'_build_deps'))
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
font=TTFont(r'C:\Windows\Fonts\NotoSerifSC-VF.ttf')
font=instantiateVariableFont(font,{'wght':600},inplace=True)
for record in font['name'].names:
    if record.nameID in (1,4,6,16):record.string='BookTitleSerif'.encode(record.getEncoding())
    elif record.nameID in (2,17):record.string='Regular'.encode(record.getEncoding())
options=subset.Options();options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
s=subset.Subsetter(options=options)
s.populate(text='深度学习与开发原理实战应用作者'+''.join(chr(i) for i in range(32,127)))
s.subset(font)
font.save(ROOT/'vendor/fonts/BookTitleSerif-600.ttf')
print('Prepared BookTitleSerif 600')
