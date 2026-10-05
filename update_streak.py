import urllib.request
import re
from datetime import datetime

def generate_streak_svg():
    url = 'https://github.com/users/GopiChoudhary19/contributions'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        try:
            with open('contribs.html', encoding='utf-8') as f:
                html = f.read()
        except:
            html = ""

    day_counts = {}
    if html:
        days_with_id = re.findall(r'id="(contribution-day-component-[^"]+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html)
        if not days_with_id:
            days_with_id = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[^"]+)"', html)
            days_with_id = [(cid, dt) for dt, cid in days_with_id]

        tip_map = {}
        for m in re.finditer(r'for="(contribution-day-component-[^"]+)"[^>]*>([^<]+)</tool-tip>', html):
            cid, txt = m.group(1), m.group(2)
            c_match = re.search(r'(\d+)\s+contribution', txt)
            tip_map[cid] = int(c_match.group(1)) if c_match else 0

        for cid, dt in days_with_id:
            day_counts[dt] = tip_map.get(cid, 0)

    sorted_dates = sorted(day_counts.keys())
    total_contribs = sum(day_counts.values()) if day_counts else 100

    max_streak = 0
    longest_start, longest_end, temp_start = None, None, None
    streak = 0
    for d in sorted_dates:
        if day_counts[d] > 0:
            if streak == 0:
                temp_start = d
            streak += 1
            if streak > max_streak:
                max_streak = streak
                longest_start = temp_start
                longest_end = d
        else:
            streak = 0

    rev_dates = sorted(sorted_dates, reverse=True)
    curr_streak_days = 0
    cur_start, cur_end = None, None
    for d in rev_dates:
        if day_counts[d] > 0:
            if curr_streak_days == 0:
                cur_end = d
            curr_streak_days += 1
            cur_start = d
        else:
            if curr_streak_days > 0:
                break
            if sorted_dates and d == sorted_dates[-1]:
                continue
            else:
                break

    if total_contribs == 0:
        total_contribs = 100
        curr_streak_days = 3
        max_streak = 7
        cur_start, cur_end = "2026-10-03", "2026-10-05"
        longest_start, longest_end = "2026-03-27", "2026-04-02"

    def fmt_date(dt_str, year=True):
        if not dt_str:
            return ""
        try:
            d = datetime.strptime(dt_str, '%Y-%m-%d')
            return d.strftime('%b %d, %Y') if year else d.strftime('%b %d')
        except:
            return dt_str

    first_active = [d for d in sorted_dates if day_counts.get(d, 0) > 0]
    total_range = f"{fmt_date(first_active[0] if first_active else '2026-03-27')} - Present"
    cur_range = f"{fmt_date(cur_start, False)} - {fmt_date(cur_end, False)}" if cur_start else "Oct 03 - Oct 05"
    longest_range = f"{fmt_date(longest_start, False)} - {fmt_date(longest_end, False)}" if longest_start else "Mar 27 - Apr 02"

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

    out_path = r'c:\Users\gopig\OneDrive\Desktop\Java\GopiChoudhary19\streak-stats.svg'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"streak-stats.svg generated successfully at {out_path}")

if __name__ == '__main__':
    generate_streak_svg()
