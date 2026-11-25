import csv,html,json
from datetime import date
from pathlib import Path
P=Path(__file__).parent
def summarize(goal,observations):
    target=float(goal['target_percent']);window=int(goal['window']);required=int(goal['required_trials'])
    if not 0<=target<=100 or not 1<=required<=window:raise ValueError('Invalid goal')
    points=[];seen=set()
    for row in observations:
        if (row['learner'],row['skill'])!=(goal['learner'],goal['skill']):continue
        d=date.fromisoformat(row['date']);c=int(row['correct']);n=int(row['opportunities'])
        if not 0<=c<=n or n==0 or d in seen:raise ValueError('Invalid or duplicate observation')
        seen.add(d);points.append((d.isoformat(),100*c/n))
    points.sort();recent=points[-window:];hits=sum(p>=target for _,p in recent)
    status='Insufficient observations' if len(recent)<window else 'Target met' if hits>=required else 'Progressing / review'
    return {'learner':goal['learner'],'skill':goal['skill'],'target':target,'hits':hits,'window':window,'status':status,'points':points}
def read(name):
    with (P/name).open() as f:return list(csv.DictReader(f))
def main():
    data=read('observations.csv');results=[summarize(g,data) for g in read('goals.csv')];(P/'results.json').write_text(json.dumps(results,indent=2))
    cards=[]
    for r in results:
        points=r['points'];coords=' '.join(f'{35+i*430/max(1,len(points)-1):.1f},{160-1.4*p:.1f}' for i,(_,p) in enumerate(points));target_y=160-1.4*r['target']
        dots=''.join(f'<circle cx="{35+i*430/max(1,len(points)-1):.1f}" cy="{160-1.4*p:.1f}" r="4" fill="#176b81"><title>{html.escape(d)}: {p:.0f}%</title></circle>' for i,(d,p) in enumerate(points))
        cards.append(f'<article><small>{html.escape(r["learner"])}</small><h2>{html.escape(r["skill"])}</h2><b>{r["status"]}</b><p>{r["hits"]} target-level observations in last {r["window"]} planned trials · target {r["target"]:.0f}%</p><svg viewBox="0 0 500 190" role="img" aria-label="Observation accuracy over time"><text x="0" y="25">100%</text><text x="0" y="164">0%</text><line x1="35" x2="465" y1="{target_y}" y2="{target_y}" stroke="#a56c36" stroke-dasharray="5 4"/><polyline points="{coords}" stroke="#176b81" fill="none" stroke-width="3"/>{dots}</svg><p>{" · ".join(f"{d[5:]}: {p:.0f}%" for d,p in points)}</p></article>')
    (P/'progress_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Learning Progress</title><style>body{font:16px system-ui;background:#eef3f8;color:#19364c}main{max-width:1050px;margin:30px auto;padding:16px}header{background:#19364c;color:white;padding:20px;border-radius:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px;margin-top:18px}article{background:white;padding:20px;border:1px solid #d4e0e9;border-radius:12px}svg{width:100%;height:auto}</style><main><header><h1>Learning progress monitor</h1><p>Fictional observations. Human review is required.</p></header><div class="grid">'+''.join(cards)+'</div></main></html>')
if __name__=='__main__':main()
