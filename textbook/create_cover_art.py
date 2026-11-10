"""Original abstract cover: interwoven signals and a sparse activation field.
No reference image, lettering, brand, stair motif or stock artwork is used.
"""
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parent
colors=['#244b64','#4a7f7a','#b7834b','#936679','#71668b']
out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 470"><title>表示与行动的交织</title>']
out.append('<defs><linearGradient id="wash" x1="0" x2="1"><stop stop-color="#eee4d3"/><stop offset="1" stop-color="#e5eeea"/></linearGradient></defs>')
out.append('<rect x="0" y="30" width="1000" height="405" fill="url(#wash)"/>')
for k in range(19):
    y=62+k*18
    end=62+((k*7)%19)*18
    col=colors[k%len(colors)]
    out.append(f'<path d="M 0 {y} C 225 {y}, 270 {425-y}, 490 {end} S 740 {y}, 1000 {y}" fill="none" stroke="{col}" stroke-width="{1.1 if k%3 else 2.5}" opacity=".64"/>')
for r in range(9):
    for c in range(9):
        x=680+c*27;y=123+r*27
        a=(r*5+c*3)%11
        col=colors[(r+c)%5]
        rad=2.3 if a>5 else 4.1
        out.append(f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{col}" opacity="{.35 if a>5 else .9}"/>')
for x,y,col in [(128,188,colors[0]),(338,216,colors[2]),(520,252,colors[1])]:
    out.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#fcfaf5" stroke="{col}" stroke-width="2.5"/><circle cx="{x}" cy="{y}" r="4" fill="{col}"/>')
out.append('</svg>')
(ROOT/'figures/cover_signal_weave.svg').write_text(''.join(out),encoding='utf-8')
print('Original vector cover artwork created.')
