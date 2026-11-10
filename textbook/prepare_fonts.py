"""Prepare a regular-weight open Song-style fallback and chart font."""
from pathlib import Path
import sys,urllib.request
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'_build_deps'))
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
dest=ROOT/'vendor/fonts';dest.mkdir(exist_ok=True)
font=TTFont(r'C:\Windows\Fonts\NotoSerifSC-VF.ttf')
font=instantiateVariableFont(font,{'wght':400},inplace=True)
texts=[(ROOT/'深度学习与AI_Agent开发.md').read_text(encoding='utf-8')]
texts += [p.read_text(encoding='utf-8-sig') for p in (ROOT/'figures').glob('*.py')]
texts += [p.read_text(encoding='utf-8-sig') for p in (ROOT/'agent_projects').glob('*.py')]
chars=''.join(texts)+''.join(chr(i) for i in range(32,127))+'−–×²αβθπλμσωΣ∑∞₀₁₂₃₄₅₆₇₈₉'
options=subset.Options();options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
sub=subset.Subsetter(options=options);sub.populate(text=chars);sub.subset(font)
font.save(dest/'NotoSerifSC-Regular.ttf')
try:
    font.flavor='woff2';font.save(dest/'NotoSerifSC-Regular.woff2')
except ImportError:pass
url='https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/LICENSE'
if not (dest/'LICENSE.txt').exists():
    with urllib.request.urlopen(url,timeout=30) as r:(dest/'LICENSE.txt').write_bytes(r.read())
print('Prepared',[(p.name,p.stat().st_size) for p in dest.iterdir()])
