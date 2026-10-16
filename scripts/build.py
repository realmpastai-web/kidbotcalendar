#!/usr/bin/env python3
"""Build static site from data/events.json into dist/."""
import json, html, datetime, pathlib, shutil
R = pathlib.Path(__file__).resolve().parent.parent
D = R/"dist"; ev = json.load(open(R/"data/events.json"))
today = datetime.date.today()
shutil.rmtree(D, ignore_errors=True); (D/"events").mkdir(parents=True)
e = lambda s: html.escape(str(s if s is not None else "TBA"))
CSS = """body{font-family:system-ui,sans-serif;max-width:960px;margin:auto;padding:1rem;color:#222}
a{color:#0b5}.card{border:1px solid #ddd;border-radius:8px;padding:.8rem;margin:.6rem 0}
.tag{display:inline-block;background:#eef;border-radius:4px;padding:0 .4rem;margin-right:.3rem;font-size:.85em}
.box{background:#fafafa;border:1px dashed #aaa;padding:.8rem;margin:1rem 0}select,input{margin:.2rem}"""
def page(title, body):
    return f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(title)} | KidBotCalendar</title><style>{CSS}</style><body><header><a href="/"><b>KidBotCalendar.in</b></a> — kids' robotics, coding &amp; Minecraft competitions in India</header>{body}
<div class=box><b>Disclosure:</b> Some links may become affiliate links (e.g. robotics kits); we may earn a small commission at no cost to you. Featured listings will always be labelled "Featured". We do not publish reviews or ratings. Data is taken from official organizer pages; always confirm on the official site.</div>
<footer><small>Built {today}. Preview — not launched.</small></footer></body></html>"""
def card(x):
    return f"""<div class="card ev" data-type="{e(x['type'])}" data-amin="{x['age_min'] or 0}" data-amax="{x['age_max'] or 99}" data-dl="{x['registration_deadline'] or ''}" data-city="{e(x['city']).lower()}">
<h3><a href="/events/{x['id']}.html">{e(x['name'])}</a></h3><span class=tag>{e(x['type'])}</span><span class=tag>{e(x['mode'])}</span><span class=tag>{e(x['status'])}</span>
<div>Ages: {e(x['age_band'])} · Where: {e(x['city'])}</div><div>{"<b>⚠ Dates unconfirmed — official pages disagree.</b> " if x.get("date_unconfirmed") else ""}Dates: {e(x["start_date"])} → {e(x['end_date'])} · Deadline: {e(x['registration_deadline'])}</div></div>"""
month = [x for x in ev if x["registration_deadline"] and x["registration_deadline"][:7]==today.isoformat()[:7]]
srt = sorted(ev, key=lambda x: x["registration_deadline"] or x["end_date"] or "9999")
filt = """<div class=box><label>Age <input id=age type=number min=4 max=22 size=3></label>
<label>Type <select id=type><option value="">All</option><option>robotics</option><option>coding</option><option>minecraft</option></select></label>
<label>City <input id=city placeholder="e.g. Bangalore, Online"></label>
<label><input id=open type=checkbox> Deadline not passed</label></div>
<script>const T="%s";function f(){const a=+age.value,t=type.value,c=city.value.toLowerCase(),o=open.checked;
document.querySelectorAll('.ev').forEach(d=>{let s=true;if(a&&(a<+d.dataset.amin||a>+d.dataset.amax))s=false;if(t&&d.dataset.type!=t)s=false;
if(c&&!d.dataset.city.includes(c))s=false;if(o&&d.dataset.dl&&d.dataset.dl<T)s=false;d.style.display=s?'':'none'})}
document.querySelectorAll('input,select').forEach(i=>i.oninput=f)</script>""" % today
body = f"""<h1>Kids' tech competitions in India</h1><p>{len(ev)} events tracked.</p>
<h2>Deadlines this month</h2>{''.join(card(x) for x in month) or '<p>No verified deadlines this month.</p>'}
<h2>All events</h2>{filt}{''.join(card(x) for x in srt)}
<div class=box><b>Weekly deadline email</b> (coming soon) <input disabled placeholder="you@example.com"><button disabled>Notify me</button></div>
<div class=box><b>Featured listing</b> placeholder — academies/organizers can sponsor a clearly-labelled spot. Not yet available.</div>"""
(D/"index.html").write_text(page("Home", body))
for x in ev:
    rows = "".join(f"<tr><th align=left>{k}</th><td>{e(x[k])}</td></tr>" for k in ["organizer","type","start_date","end_date","registration_deadline","fee","age_band","city","mode","status","notes","last_checked"])
    src = " ".join(f'<a href="{e(u)}" rel=nofollow>{e(u)}</a>' for u in x["source_urls"])
    (D/f"events/{x['id']}.html").write_text(page(x["name"], f"<h1>{e(x['name'])}</h1><table>{rows}</table><p><a href=\"{e(x['url'])}\">Official page →</a></p><p><small>Sources: {src}</small></p>"))
print(f"built {len(ev)} events, {len(month)} deadlines this month")
