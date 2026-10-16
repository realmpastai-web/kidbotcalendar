#!/usr/bin/env python3
"""Re-check each source URL: reachability + whether key facts (dates) still appear. Writes data/check_report.json,
bumps last_checked for reachable rows, flags changes for human/agent review (never auto-edits facts). Then rebuilds."""
import json, re, datetime, pathlib, urllib.request, hashlib, subprocess, sys
R = pathlib.Path(__file__).resolve().parent.parent; P = R/"data/events.json"
ev = json.load(open(P)); prev = {}
hp = R/"data/hashes.json"; prev = json.load(open(hp)) if hp.exists() else {}
rep, today = [], datetime.date.today().isoformat()
for x in ev:
    for u in x["source_urls"]:
        r = {"id": x["id"], "url": u}
        try:
            t = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 KidBotCalendar-checker"}), timeout=25).read().decode("utf8", "ignore")
            txt = re.sub(r"<[^>]+>", " ", t); h = hashlib.sha256(re.sub(r"\s+", " ", txt).encode()).hexdigest()
            r.update(ok=True, changed=prev.get(u) not in (None, h)); prev[u] = h
            r["years_seen"] = sorted(set(re.findall(r"\b202[6-9]\b", txt)))
            x["last_checked"] = today
        except Exception as ex:
            r.update(ok=False, error=str(ex)[:200])
        rep.append(r)
json.dump(ev, open(P, "w"), indent=1, ensure_ascii=False); json.dump(prev, open(hp, "w"), indent=1)
json.dump({"checked": today, "results": rep}, open(R/"data/check_report.json", "w"), indent=1)
print(f"{sum(r['ok'] for r in rep)}/{len(rep)} reachable; changed: {[r['id'] for r in rep if r.get('changed')]}")
subprocess.run([sys.executable, str(R/"scripts/build.py")], check=True)
