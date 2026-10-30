#!/usr/bin/env python3
"""Build static site from data/events.json into dist/."""
import json, html, datetime, pathlib, shutil, re
R = pathlib.Path(__file__).resolve().parent.parent
D = R/"dist"; ev = json.load(open(R/"data/events.json"))
today = datetime.date.today()
shutil.rmtree(D, ignore_errors=True); (D/"events").mkdir(parents=True)
e = lambda s: html.escape(str(s if s is not None else "TBA"))
CSS = """body{font-family:system-ui,sans-serif;max-width:960px;margin:auto;padding:1rem;color:#222}
a{color:#0b5}.card{border:1px solid #ddd;border-radius:8px;padding:.8rem;margin:.6rem 0}
.tag{display:inline-block;background:#eef;border-radius:4px;padding:0 .4rem;margin-right:.3rem;font-size:.85em}
.box{background:#fafafa;border:1px dashed #aaa;padding:.8rem;margin:1rem 0}select,input{margin:.2rem}"""
SITE = "https://kidbotcalendar.in/"
def page(title, body, p="", desc="", path=""):
    desc = desc or "Upcoming kids' robotics, coding and Minecraft competitions in India, with dates, deadlines, fees and ages from official organizer pages."
    return f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(title)} | KidBotCalendar</title><meta name=description content="{e(desc)}"><link rel=canonical href="{SITE}{path}"><style>{CSS}</style><body><header><a href="{p}index.html"><b>KidBotCalendar.in</b></a> — kids' robotics, coding &amp; Minecraft competitions in India</header>{body}
<div class=box><b>Disclosure:</b> Some links may become affiliate links (e.g. robotics kits); we may earn a small commission at no cost to you. Featured listings will always be labelled "Featured". We do not publish reviews or ratings. Data is taken from official organizer pages; always confirm on the official site.</div>
<footer><small>Built {today}. Preview — not launched.</small></footer></body></html>"""
def card(x, p=""):
    return f"""<div class="card ev" data-type="{e(x['type'])}" data-amin="{x['age_min'] or 0}" data-amax="{x['age_max'] or 99}" data-dl="{x['registration_deadline'] or ''}" data-city="{e(x['city']).lower()}">
<h3><a href="{p}events/{x['id']}.html">{e(x['name'])}</a></h3><span class=tag>{e(x['type'])}</span><span class=tag>{e(x['mode'])}</span><span class=tag>{e(x['status'])}</span>
<div>Ages: {e(x['age_band'])} · Where: {e(x['city'])}</div><div>{"<b>⚠ Dates unconfirmed — official pages disagree.</b> " if x.get("date_unconfirmed") else ""}Dates: {e(x["start_date"])} → {e(x['end_date'])} · Deadline: {e(x['registration_deadline'])}</div></div>"""
def past(x):  # event over: end (or start) date before today, or marked completed
    d = x["end_date"] or x["start_date"]
    return x["status"] == "completed" or (d is not None and d < today.isoformat())
up = [x for x in ev if not past(x)]; old = [x for x in ev if past(x)]
srt = sorted(up, key=lambda x: x["registration_deadline"] if (x["registration_deadline"] or "") >= today.isoformat() else (x["start_date"] or x["end_date"] or "9999"))
ym = today.isoformat()[:7]
month = [x for x in up if (x["registration_deadline"] or "")[:7] == ym and x["registration_deadline"] >= today.isoformat()]
def months():  # this month + next two months
    y, m = today.year, today.month
    for _ in range(3):
        yield datetime.date(y, m, 1)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
def mslug(d): return f"deadlines-{d.strftime('%B').lower()}-{d.year}.html"
filt = """<div class=box><label>Age <input id=age type=number min=4 max=22 size=3></label>
<label>Type <select id=type><option value="">All</option><option>robotics</option><option>coding</option><option>minecraft</option></select></label>
<label>City <input id=city placeholder="e.g. Bangalore, Online"></label>
<label><input id=open type=checkbox> Deadline not passed</label></div>
<script>const T="%s";function f(){const a=+age.value,t=type.value,c=city.value.toLowerCase(),o=open.checked;
document.querySelectorAll('.ev').forEach(d=>{let s=true;if(a&&(a<+d.dataset.amin||a>+d.dataset.amax))s=false;if(t&&d.dataset.type!=t)s=false;
if(c&&!d.dataset.city.includes(c))s=false;if(o&&d.dataset.dl&&d.dataset.dl<T)s=false;d.style.display=s?'':'none'})}
document.querySelectorAll('input,select').forEach(i=>i.oninput=f)</script>""" % today
TYPES = {"robotics": "Robotics", "coding": "Coding", "minecraft": "Minecraft"}
nav = "<p>Browse: " + " · ".join([f'<a href="{mslug(d)}">Deadlines {d.strftime("%B %Y")}</a>' for d in months()] +
      [f'<a href="{k}-competitions.html">{v}</a>' for k, v in TYPES.items()] + ['<a href="online-competitions.html">Online</a>', '<a href="free-competitions.html">Free</a>', '<a href="free-online-competitions.html">Free &amp; online</a>', '<a href="registration-open.html">Registration open</a>', '<a href="closing-soon.html">Closing in 30 days</a>', '<a href="competitions-in-bangalore.html">Bangalore</a>', '<a href="competitions-in-delhi-ncr.html">Delhi NCR</a>', '<a href="competitions-in-chennai.html">Chennai</a>', '<a href="competitions-in-hyderabad.html">Hyderabad</a>', '<a href="competitions-in-pune.html">Pune</a>', '<a href="competitions-in-mumbai.html">Mumbai</a>', '<a href="competitions-in-kolkata.html">Kolkata</a>', '<a href="competitions-by-age.html">By age</a>', '<a href="olympiads.html">Olympiads</a>', '<a href="ai-competitions.html">AI competitions</a>', '<a href="innovation-challenges.html">Innovation &amp; hackathons</a>', '<a href="scratch-coding-competitions.html">Scratch &amp; block coding</a>', '<a href="past-events.html">Past events</a>']) + "</p>"
body = f"""<h1>Kids' tech competitions in India</h1><p>{len(up)} upcoming events tracked ({len(old)} past, see <a href="past-events.html">archive</a>).</p>{nav}
<h2>Deadlines this month</h2>{''.join(card(x) for x in month) or '<p>No verified deadlines this month.</p>'}
<h2>Upcoming events</h2>{filt}{''.join(card(x) for x in srt)}
<div class=box><b>Weekly deadline email</b> (coming soon) <input disabled placeholder="you@example.com"><button disabled>Notify me</button></div>
<div class=box><b>Featured listing</b> placeholder — academies/organizers can sponsor a clearly-labelled spot. Not yet available.</div>"""
pages = [("index.html", "Kids' robotics, coding & Minecraft competitions in India", body, "")]
for d in months():
    k = d.isoformat()[:7]; mn = d.strftime("%B %Y")
    dl = sorted([x for x in up if (x["registration_deadline"] or "")[:7] == k and x["registration_deadline"] >= today.isoformat()], key=lambda x: x["registration_deadline"])
    on = sorted([x for x in up if x["start_date"] and x["start_date"][:7] <= k <= (x["end_date"] or x["start_date"])[:7]], key=lambda x: x["start_date"])
    b = f"""<h1>Kids' robotics &amp; coding competition deadlines: {mn}</h1><p>Registration and submission deadlines falling in {mn} for kids' robotics, coding and Minecraft competitions in India, from official organizer pages. Always confirm on the official site.</p>{nav}
<h2>Deadlines in {mn} ({len(dl)})</h2>{''.join(card(x) for x in dl) or '<p>No verified deadlines in this month yet.</p>'}
<h2>Competitions happening in {mn} ({len(on)})</h2>{''.join(card(x) for x in on) or '<p>No verified competition dates in this month yet.</p>'}"""
    pages.append((mslug(d), f"Competition deadlines {mn}", b, f"Kids' robotics, coding and Minecraft competition deadlines in India for {mn}: {len(dl)} verified deadlines and {len(on)} events, with dates, fees and ages."))
for k, v in TYPES.items():
    L = [x for x in srt if x["type"] == k]
    pages.append((f"{k}-competitions.html", f"{v} competitions for kids in India", f"<h1>Upcoming {v.lower()} competitions for kids in India</h1>{nav}{''.join(card(x) for x in L) or '<p>No verified upcoming events right now.</p>'}",
                  f"{len(L)} upcoming {v.lower()} competitions for school kids in India with dates, deadlines, fees and age groups from official organizer pages."))
L = [x for x in srt if x["mode"] in ("online", "hybrid")]
pages.append(("online-competitions.html", "Online robotics & coding competitions for kids in India", f"<h1>Online &amp; hybrid kids' tech competitions (India)</h1><p>Events kids can enter online from anywhere in India.</p>{nav}{''.join(card(x) for x in L)}",
              f"{len(L)} online or hybrid robotics, coding and Minecraft competitions open to kids in India, with deadlines and ages."))
CITIES = {"bangalore": ("Bangalore (Bengaluru)", ["bangalore", "bengaluru"]), "chennai": ("Chennai", ["chennai"]),
          "delhi-ncr": ("Delhi NCR", ["delhi", "noida", "gurugram"]), "hyderabad": ("Hyderabad", ["hyderabad"]),
          "pune": ("Pune", ["pune"]), "mumbai": ("Mumbai", ["mumbai"]), "kolkata": ("Kolkata", ["kolkata"])}
for k, (v, keys) in CITIES.items():
    L = [x for x in srt if any(w in ((x["city"] or "") + " " + (x["notes"] or "")).lower() for w in keys)]
    if not L: continue
    pages.append((f"competitions-in-{k}.html", f"Kids' robotics & coding competitions in {v}", f"<h1>Kids' robotics, coding &amp; Minecraft competitions in {e(v)}</h1><p>Upcoming competitions with a venue, zonal round or exam centre in {e(v)}, as named on the official organizer page. Online events are listed <a href=\"online-competitions.html\">separately</a>. Always confirm venue and dates on the official site.</p>{nav}{''.join(card(x) for x in L)}",
                  f"{len(L)} upcoming kids' robotics, coding and Minecraft competitions with rounds or venues in {v}, with dates, deadlines, fees and ages from official pages."))
AGES = [(6, 10), (11, 14), (15, 18)]
ab = [f'<h1>Kids\' robotics, coding &amp; Minecraft competitions in India by age</h1><p>Upcoming competitions grouped by the age range on the official page (where an organizer lists only school grades/classes, ages are approximated). An event appears in every group its age range overlaps. Events with no published age range are not listed here.</p>{nav}']
for lo, hi in AGES:
    L = [x for x in srt if x["age_min"] is not None and x["age_min"] <= hi and (x["age_max"] if x["age_max"] is not None else 99) >= lo]
    ab.append(f'<h2 id="ages-{lo}-{hi}">Ages {lo}-{hi} ({len(L)})</h2>' + (''.join(card(x) for x in L) or '<p>No verified upcoming events for this age group.</p>'))
pages.append(("competitions-by-age.html", "Kids' robotics & coding competitions by age (6-10, 11-14, 15-18)", "".join(ab),
              "Upcoming robotics, coding and Minecraft competitions in India for ages 6-10, 11-14 and 15-18, with dates, deadlines and fees from official organizer pages."))
L = [x for x in srt if re.search(r"olympiad", x["name"], re.I)]
pages.append(("olympiads.html", "Robotics, coding & AI olympiads for school students in India", f"<h1>Robotics, coding &amp; AI olympiads for school students in India</h1><p>Upcoming competitions that call themselves an olympiad on the official organizer page, sorted by next deadline or date. Some are national selection routes to international olympiads (e.g. informatics, AI); others are organizer-run olympiads. Always confirm dates, fees and eligibility on the official site.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified upcoming olympiads right now.</p>'}",
              f"{len(L)} upcoming robotics, coding and AI olympiads for school students in India, with dates, deadlines, fees and ages from official organizer pages."))
L = [x for x in srt if re.search(r"\bAI\b|artificial intelligence", x["name"] + " " + (x["notes"] or ""), re.I)]
pages.append(("ai-competitions.html", "AI competitions & olympiads for school kids in India", f"<h1>AI competitions &amp; olympiads for school kids in India</h1><p>Upcoming competitions whose official page names artificial intelligence (AI) as a focus. Always confirm dates, fees and eligibility on the official site.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified upcoming AI competitions right now.</p>'}",
              f"{len(L)} upcoming AI competitions and olympiads for school students in India, with dates, fees and age groups from official organizer pages."))
L = [x for x in srt if re.search(r"makeathon|hackathon|innovation|innovator|\\bchallenge\\b", x["name"] + " " + (x["notes"] or ""), re.I)]
pages.append(("innovation-challenges.html", "School innovation challenges & hackathons for kids in India", f"<h1>School innovation challenges, makeathons &amp; hackathons for kids in India</h1><p>Upcoming project-based competitions where students build and present a prototype, app or invention, as described on the official organizer page (makeathons, hackathons, innovation challenges). Always confirm dates, fees and eligibility on the official site.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified upcoming innovation challenges right now.</p>'}",
              f"{len(L)} upcoming school innovation challenges, makeathons and hackathons for kids in India, with dates, deadlines and ages from official organizer pages."))
L = [x for x in srt if re.search(r"scratch|pictoblox|app inventor|block[- ]based|block coding", x["name"] + " " + (x["notes"] or ""), re.I)]
pages.append(("scratch-coding-competitions.html", "Scratch & block coding competitions for kids in India", f"<h1>Scratch, PictoBlox &amp; block coding competitions for kids in India</h1><p>Upcoming competitions whose official page names Scratch, PictoBlox, MIT App Inventor or block-based coding as a platform, good first contests for younger coders. Always confirm dates, fees and eligibility on the official site.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified upcoming Scratch or block coding competitions right now.</p>'}",
              f"{len(L)} upcoming Scratch, PictoBlox and block coding competitions for kids in India, with dates, deadlines, fees and ages from official organizer pages."))
L = [x for x in srt if (x["fee"] or "").lower().startswith("free")]
pages.append(("free-competitions.html", "Free robotics & coding competitions for kids in India", f"<h1>Free kids' robotics &amp; coding competitions in India</h1><p>Upcoming competitions whose official page lists the entry as free. Kits, hardware or software may still cost money; check each event's notes.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified free events right now.</p>'}",
              f"{len(L)} free-to-enter robotics, coding and Minecraft competitions for school kids in India, verified on official organizer pages."))
L = [x for x in srt if (x["fee"] or "").lower().startswith("free") and x["mode"] in ("online", "hybrid")]
pages.append(("free-online-competitions.html", "Free online coding, robotics & Minecraft competitions for kids in India", f"<h1>Free online coding, robotics &amp; Minecraft competitions for kids in India</h1><p>Upcoming competitions whose official page lists entry as free <i>and</i> that can be taken online or in hybrid mode, so kids anywhere in India can join without travel or an entry fee. Some still need a school/teacher to register, or software access (check each event's notes). Always confirm on the official site.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified free online events right now.</p>'}",
              f"{len(L)} free online and hybrid coding, robotics and Minecraft competitions for school kids in India, with deadlines and ages from official organizer pages."))
L = sorted([x for x in up if x["status"] == "registration-open" and (x["registration_deadline"] or "9999") >= today.isoformat()], key=lambda x: x["registration_deadline"] or "9999")
pages.append(("registration-open.html", "Kids' robotics & coding competitions with registration open now (India)", f"<h1>Kids' robotics, coding &amp; Minecraft competitions with registration open now</h1><p>Competitions whose official page shows registration as open and whose deadline (if published) has not passed, soonest deadline first. Events with no published deadline are listed last. Always confirm on the official site before paying or travelling.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified open registrations right now.</p>'}",
              f"{len(L)} kids' robotics, coding and Minecraft competitions in India with registration open now, sorted by deadline, from official organizer pages."))
soon = (today + datetime.timedelta(days=30)).isoformat()
L = sorted([x for x in up if today.isoformat() <= (x["registration_deadline"] or "") <= soon], key=lambda x: x["registration_deadline"])
pages.append(("closing-soon.html", "Kids' robotics & coding competition deadlines in the next 30 days (India)", f"<h1>Kids' robotics, coding &amp; Minecraft competitions closing in the next 30 days</h1><p>Competitions whose official registration or submission deadline falls between {today.strftime('%-d %B %Y')} and {(today + datetime.timedelta(days=30)).strftime('%-d %B %Y')}, soonest first. Events with no published deadline are not listed; see <a href=\"registration-open.html\">registration open</a>. Always confirm the deadline on the official site.</p>{nav}{''.join(card(x) for x in L) or '<p>No verified deadlines in the next 30 days.</p>'}",
              f"{len(L)} kids' robotics, coding and Minecraft competitions in India with registration or submission deadlines in the next 30 days, soonest first, from official organizer pages."))
pages.append(("past-events.html", "Past kids' tech competitions (archive)", f"<h1>Past events (archive)</h1><p>Events whose dates have passed. Kept for reference; check the organizer for next season.</p>{nav}{''.join(card(x) for x in sorted(old, key=lambda x: x['end_date'] or '', reverse=True)) or '<p>None yet.</p>'}",
              "Archive of past kids' robotics, coding and Minecraft competitions in India tracked by KidBotCalendar."))
for fn, t, b, dsc in pages:
    (D/fn).write_text(page(t, b, desc=dsc, path="" if fn == "index.html" else fn))
for x in ev:
    rows = "".join(f"<tr><th align=left>{k}</th><td>{e(x[k])}</td></tr>" for k in ["organizer","type","start_date","end_date","registration_deadline","fee","age_band","city","mode","status","notes","last_checked"])
    src = " ".join(f'<a href="{e(u)}" rel=nofollow>{e(u)}</a>' for u in x["source_urls"])
    (D/f"events/{x['id']}.html").write_text(page(x["name"], f"{'<p><b>This event is over (archived).</b></p>' if past(x) else ''}<h1>{e(x['name'])}</h1><table>{rows}</table><p><a href=\"{e(x['url'])}\">Official page →</a></p><p><small>Sources: {src}</small></p>", "../", f"{x['name']}: dates, registration deadline, fee, ages and location, from the official organizer page.", f"events/{x['id']}.html"))
(D/"CNAME").write_text("kidbotcalendar.in\n")
(D/"googled5324eca40acbf99.html").write_text("google-site-verification: googled5324eca40acbf99.html")  # Search Console
urls = [fn for fn, *_ in pages] + [f"events/{x['id']}.html" for x in ev]
(D/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{'' if u == 'index.html' else u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
(D/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
print(f"built {len(ev)} events ({len(up)} upcoming, {len(old)} past), {len(month)} deadlines this month, {len(pages)} pages + sitemap")
