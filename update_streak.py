import json
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone

USER = "GopiChoudhary19"
API = "https://api.github.com/graphql"


def gql(query, variables):
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": f"bearer {token}", "User-Agent": USER})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


def contribution_days():
    created = gql("query($u:String!){user(login:$u){createdAt}}", {"u": USER})["user"]["createdAt"]
    start = datetime.fromisoformat(created.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    q = """query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){contributionsCollection(from:$f,to:$t){
      contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    days = {}
    while start < now:
        stop = min(start + timedelta(days=365), now)
        cal = gql(q, {"u": USER, "f": start.isoformat(), "t": stop.isoformat()})
        for w in cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        start = stop
    today = now.date().isoformat()
    return {k: v for k, v in days.items() if k <= today}


def top_languages(n=6):
    q = """query($u:String!){user(login:$u){repositories(first:100,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){nodes{
      name languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}"""
    totals, colors = {}, {}
    for repo in gql(q, {"u": USER})["user"]["repositories"]["nodes"]:
        if repo["name"] == USER:
            continue
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            totals[name] = totals.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or "#8b949e"
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])[:n]
    s = sum(v for _, v in ranked) or 1
    return [(k, v / s * 100, colors[k]) for k, v in ranked]


def streaks(day_counts):
    dates = sorted(day_counts)
    longest, run, run_start, longest_span = 0, 0, None, (None, None)
    for d in dates:
        if day_counts[d] > 0:
            run_start = d if run == 0 else run_start
            run += 1
            if run > longest:
                longest, longest_span = run, (run_start, d)
        else:
            run = 0
    # today with zero contributions does not break the current streak yet
    rev = dates[::-1]
    if rev and day_counts[rev[0]] == 0:
        rev = rev[1:]
    cur, cur_start, cur_end = 0, None, None
    for d in rev:
        if day_counts[d] == 0:
            break
        cur_end = cur_end or d
        cur_start = d
        cur += 1
    return cur, (cur_start, cur_end), longest, longest_span


def fmt_date(dt_str, year=True):
    d = datetime.strptime(dt_str, "%Y-%m-%d")
    return d.strftime("%b %d, %Y") if year else d.strftime("%b %d")


def span(a, b):
    return f"{fmt_date(a, False)} - {fmt_date(b, False)}" if a else "No active streak"


def generate_streak_svg(day_counts):
    total_contribs = sum(day_counts.values())
    curr_streak_days, (cur_start, cur_end), max_streak, (longest_start, longest_end) = streaks(day_counts)
    first_active = [d for d in sorted(day_counts) if day_counts[d] > 0]
    total_range = f"{fmt_date(first_active[0])} - Present" if first_active else "No contributions yet"
    cur_range = span(cur_start, cur_end)
    longest_range = span(longest_start, longest_end)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 495 195" width="495px" height="195px">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0e1017"/>
      <stop offset="100%" stop-color="#141321"/>
    </linearGradient>
    <linearGradient id="pinkGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fe428e"/>
      <stop offset="100%" stop-color="#ff6b9d"/>
    </linearGradient>
    <linearGradient id="topBorder" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fe428e"/>
      <stop offset="50%" stop-color="#a855f7"/>
      <stop offset="100%" stop-color="#a9fef7"/>
    </linearGradient>
  </defs>

  <style>
    .val {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 28px;
      font-weight: 800;
      fill: #fe428e;
    }}
    .label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 13px;
      font-weight: 600;
      fill: #a9fef7;
      letter-spacing: 0.3px;
    }}
    .sub {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 11px;
      font-weight: 500;
      fill: #8b949e;
    }}
    .ring {{
      fill: none;
      stroke: #fe428e;
      stroke-width: 4;
      stroke-linecap: round;
    }}
    .ring-bg {{
      fill: none;
      stroke: #2a2b40;
      stroke-width: 4;
    }}
  </style>

  <!-- Background -->
  <rect width="495" height="195" rx="8" fill="url(#cardBg)"/>
  <rect width="495" height="195" rx="8" fill="none" stroke="#252736" stroke-width="1.5"/>
  <rect x="0" y="0" width="495" height="3" rx="1.5" fill="url(#topBorder)"/>

  <!-- Column Dividers -->
  <line x1="165" y1="25" x2="165" y2="170" stroke="#212433" stroke-width="1.5"/>
  <line x1="330" y1="25" x2="330" y2="170" stroke="#212433" stroke-width="1.5"/>

  <!-- Left Column: Total Contributions -->
  <g transform="translate(82.5, 0)">
    <!-- Ring / Icon Indicator -->
    <circle cx="0" cy="52" r="22" class="ring-bg"/>
    <circle cx="0" cy="52" r="22" class="ring" stroke-dasharray="100, 138"/>
    <!-- Contribution Layers Icon -->
    <path d="M -8,52 L 0,47 L 8,52 L 0,57 Z M -8,56 L 0,61 L 8,56 M -8,60 L 0,65 L 8,60" fill="none" stroke="#fe428e" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>

    <text x="0" y="105" text-anchor="middle" class="val">{total_contribs}</text>
    <text x="0" y="132" text-anchor="middle" class="label">Total Contributions</text>
    <text x="0" y="156" text-anchor="middle" class="sub">{total_range}</text>
  </g>

  <!-- Middle Column: Current Streak (Featured) -->
  <g transform="translate(247.5, 0)">
    <!-- Fire Ring -->
    <circle cx="0" cy="52" r="24" class="ring-bg"/>
    <circle cx="0" cy="52" r="24" class="ring" stroke="url(#pinkGrad)" stroke-width="4.5" stroke-dasharray="125, 150"/>
    <!-- Fire Icon -->
    <path d="M 0,40 C 3,45 6,48 6,52 C 6,57 2,61 -1,61 C -4,61 -7,58 -7,54 C -7,49 -4,46 -3,43 C -1,46 0,49 1,51 C 2,49 1,44 0,40 Z" fill="#fe428e"/>
    <path d="M 0,49 C 1,51 2,53 2,55 C 2,57 0,59 -1,59 C -2,59 -4,58 -4,56 C -4,54 -2,52 -1,51 Z" fill="#a9fef7"/>

    <text x="0" y="105" text-anchor="middle" class="val">{curr_streak_days} Days</text>
    <text x="0" y="132" text-anchor="middle" class="label">Current Streak</text>
    <text x="0" y="156" text-anchor="middle" class="sub">{cur_range}</text>
  </g>

  <!-- Right Column: Longest Streak -->
  <g transform="translate(412.5, 0)">
    <!-- Trophy Ring -->
    <circle cx="0" cy="52" r="22" class="ring-bg"/>
    <circle cx="0" cy="52" r="22" class="ring" stroke-dasharray="115, 138"/>
    <!-- Lightning Bolt / Star Icon -->
    <path d="M 1,42 L -6,53 L -1,53 L -2,62 L 6,50 L 1,50 Z" fill="#fe428e"/>

    <text x="0" y="105" text-anchor="middle" class="val">{max_streak} Days</text>
    <text x="0" y="132" text-anchor="middle" class="label">Longest Streak</text>
    <text x="0" y="156" text-anchor="middle" class="sub">{longest_range}</text>
  </g>
</svg>'''

    with open("streak-stats.svg", "w", encoding="utf-8") as f:
        f.write(svg)


def generate_langs_svg(langs):
    rows, bar, x = [], [], 25.0
    for i, (name, pct, color) in enumerate(langs):
        w = 445 * pct / 100
        bar.append(f'<rect x="{x:.2f}" y="58" width="{w:.2f}" height="8" fill="{color}"/>')
        x += w
        cx, cy = 25 + (i % 2) * 230, 95 + (i // 2) * 26
        rows.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{color}"/>'
                    f'<text x="{cx + 16}" y="{cy}" class="lang">{name} <tspan class="pct">{pct:.1f}%</tspan></text>')
    h = 95 + ((len(langs) + 1) // 2) * 26
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 495 {h}" width="495px" height="{h}px">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0e1017"/><stop offset="100%" stop-color="#141321"/></linearGradient>
    <linearGradient id="topBorder" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#fe428e"/><stop offset="50%" stop-color="#a855f7"/><stop offset="100%" stop-color="#a9fef7"/></linearGradient>
    <clipPath id="barClip"><rect x="25" y="58" width="445" height="8" rx="4"/></clipPath>
  </defs>
  <style>
    .title {{ font: 700 18px -apple-system, "Segoe UI", Roboto, sans-serif; fill: #fe428e; }}
    .lang {{ font: 600 13px -apple-system, "Segoe UI", Roboto, sans-serif; fill: #a9fef7; }}
    .pct {{ fill: #8b949e; font-weight: 500; }}
  </style>
  <rect width="495" height="{h}" rx="8" fill="url(#cardBg)"/>
  <rect width="495" height="{h}" rx="8" fill="none" stroke="#252736" stroke-width="1.5"/>
  <rect x="0" y="0" width="495" height="3" rx="1.5" fill="url(#topBorder)"/>
  <text x="25" y="38" class="title">Most Used Languages</text>
  <g clip-path="url(#barClip)">{"".join(bar)}</g>
  {"".join(rows)}
</svg>'''
    with open("top-langs.svg", "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    generate_streak_svg(contribution_days())
    generate_langs_svg(top_languages())
