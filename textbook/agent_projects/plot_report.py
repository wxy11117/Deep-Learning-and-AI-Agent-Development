"""Generate report graphics from the same verified aggregates used in the report."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'_build_deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from analysis_tools import AnalysisStore
font_manager.fontManager.addfont(str(ROOT/'vendor/fonts/NotoSerifSC-Regular.ttf'))
plt.rcParams.update({'font.family':['Noto Serif SC','DejaVu Serif'],'axes.unicode_minus':False,'pdf.fonttype':42,'svg.fonttype':'path','axes.spines.top':False,'axes.spines.right':False})
rows=AnalysisStore().aggregate('orders','region')['rows']
fig,ax=plt.subplots(figsize=(7,3.5),layout='constrained')
colors=['#0072B2','#009E73','#CC79A7'];bars=ax.bar([r['group'] for r in rows],[float(r['profit']) for r in rows],color=colors)
ax.bar_label(bars,fmt='%.2f',padding=4);ax.set_ylim(0,235);ax.set_ylabel('利润 / 教学货币单位');ax.set_title('教学订单：各地区利润（人工构造数据）');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
out=Path(__file__).resolve().parent/'results'
for ext in ['png','pdf','svg']:fig.savefig(out/f'orders_chart.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig)
report=out/'orders_report.md';text=report.read_text(encoding='utf-8')
if 'orders_chart.png' not in text:report.write_text(text+'\n![各地区利润，人工构造数据](orders_chart.png)\n',encoding='utf-8')
print('Generated three report chart formats')


