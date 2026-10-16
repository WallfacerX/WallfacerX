#!/usr/bin/env python3
"""Generate self-contained SVGs using only Python's standard library."""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import random
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
COLORS = ['#18212e', '#304864', '#426f98', '#36b5cd', '#91f6fa']


def svg_start(width, height, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>']


def header(animated=True):
    rng = random.Random(42)
    p = svg_start(1000, 280, 'Kenyon Melton | Developer · Cybersecurity Student', 'Cyan digital rain with violet trails. The name and subtitle stay stationary. Motion stops when reduced motion is preferred.')
    p += ['<defs><radialGradient id="shade"><stop stop-color="#070a13" stop-opacity="1"/><stop offset=".7" stop-color="#070a13" stop-opacity=".97"/><stop offset="1" stop-color="#070a13" stop-opacity="0"/></radialGradient><clipPath id="frame"><rect width="1000" height="280" rx="16"/></clipPath></defs>',
          '<style>text{font-family:monospace}.stream{animation:fall var(--speed) linear infinite}@keyframes fall{from{transform:translateY(-360px)}to{transform:translateY(0)}}@media(prefers-reduced-motion:reduce){.stream{animation:none!important}}</style>' if animated else '',
          '<g clip-path="url(#frame)"><rect width="1000" height="280" fill="#05080f"/>']
    for col in range(50):
        p.append(f'<g class="stream" style="--speed:{rng.uniform(5, 13):.2f}s;animation-delay:-{rng.uniform(0, 13):.2f}s" font-size="13">')
        glyphs = [rng.choice('01{}[]<>/+=:;ABCDEF') for _ in range(20)]
        for row in range(40):
            n = row % 20
            color = '#dbffff' if n == 19 else '#48e4ee' if n > 13 else '#9a6ae8'
            opacity = .85 if n == 19 else .14 + n / 40
            p.append(f'<text x="{col*21}" y="{row*18}" fill="{color}" opacity="{opacity:.2f}">{html.escape(glyphs[n])}</text>')
        p.append('</g>')
    p += ['<ellipse cx="500" cy="140" rx="390" ry="155" fill="url(#shade)"/>',
          '<path d="M350 85H650" stroke="#9e70f5" stroke-opacity=".6"/>',
          '<text x="500" y="143" text-anchor="middle" fill="#effdff" font-size="46" font-weight="700" letter-spacing="1">Kenyon Melton</text>',
          '<text x="500" y="184" text-anchor="middle" fill="#9debf2" font-size="19">Developer · Cybersecurity Student</text>',
          '<path d="M425 209H575" stroke="#47dce9" stroke-width="2"/>', '</g></svg>']
    return ''.join(p)


class CalendarParser(HTMLParser):
    """Optional public GitHub HTML import for local previews without credentials."""
    def __init__(self):
        super().__init__()
        self.days = {}
        self.tip = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and 'data-date' in a:
            self.days[a['id']] = {'date': a['data-date'], 'level': int(a['data-level'])}
        if tag == 'tool-tip':
            self.tip = a.get('for')
    def handle_data(self, data):
        if self.tip in self.days and 'contribution' in data:
            m = re.search(r'([\d,]+) contributions?', data)
            self.days[self.tip]['contributionCount'] = int(m[1].replace(',', '')) if m else 0
    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip = None


def fetch_calendar(public_html=None):
    if public_html:
        parser = CalendarParser()
        parser.feed(Path(public_html).read_text())
        days = sorted(parser.days.values(), key=lambda d: d['date'])
    else:
        query = 'query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount contributionLevel}}}}}}'
        req = urllib.request.Request('https://api.github.com/graphql', data=json.dumps({'query': query, 'variables': {'login': 'WallfacerX'}}).encode(), headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Content-Type': 'application/json', 'User-Agent': 'WallfacerX-profile-animations'})
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.load(response)
        if result.get('errors'):
            raise RuntimeError(result['errors'])
        levels = ['NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE']
        days = [{**d, 'level': levels.index(d['contributionLevel'])} for w in result['data']['user']['contributionsCollection']['contributionCalendar']['weeks'] for d in w['contributionDays']]
    validate(days)
    return days


def validate(days):
    if not 350 <= len(days) <= 372:
        raise ValueError('Incomplete contribution calendar; preserving previous assets')
    dates = [dt.date.fromisoformat(d['date']) for d in days]
    if any((b-a).days != 1 for a,b in zip(dates, dates[1:])):
        raise ValueError('Calendar must contain consecutive, unique dates')
    if any(not isinstance(d['contributionCount'], int) or d['contributionCount'] < 0 or d['level'] not in range(5) for d in days):
        raise ValueError('Invalid contribution counts or levels')


def contribution_svg(days, animated=True):
    first = dt.date.fromisoformat(days[0]['date'])
    origin = first - dt.timedelta(days=(first.weekday()+1)%7)
    cells = []
    for d in days:
        offset = (dt.date.fromisoformat(d['date'])-origin).days
        cells.append((offset//7, offset%7, d))
    route = sorted(cells, key=lambda c:(c[0], c[1] if c[0]%2 == 0 else -c[1]))
    arrivals = {d['date']: i for i, (_, _, d) in enumerate(route)}
    total = sum(d['contributionCount'] for d in days)
    p = svg_start(1000, 238, 'Contribution arcade | WallfacerX', f'{total} real contributions from {days[0]["date"]} to {days[-1]["date"]}. A Pac-Man-style character eats active day squares. This is a separate visualization of GitHub data.')
    css = ['text{font-family:monospace}', '.player{display:none}']
    duration = 65
    if animated:
        css += [f'.player{{display:inline;animation:travel {duration}s linear infinite}}', f'.mouth{{animation:chomp .22s steps(2,end) infinite}}', '@keyframes chomp{50%{transform:scaleY(.2)}}']
        keyframes = []
        for i, (col, row, _) in enumerate(route):
            keyframes.append(f'{i/(len(route)-1)*94:.5f}%{{transform:translate({32+col*18}px,{83+row*18}px)}}')
        col,row,_ = route[-1]
        keyframes.append(f'100%{{transform:translate({32+col*18}px,{83+row*18}px)}}')
        css.append('@keyframes travel{'+''.join(keyframes)+'}')
        for _, _, d in cells:
            if not d['contributionCount']:
                continue
            t = arrivals[d['date']]/(len(route)-1)*94
            css.append(f'.d{arrivals[d["date"]]}{{animation:e{arrivals[d["date"]]} {duration}s linear infinite}}@keyframes e{arrivals[d["date"]]}{{0%,{max(0,t-.001):.5f}%{{fill:{COLORS[d["level"]]};opacity:1}}{max(.001,t):.5f}%,98%{{fill:#9a6ae8;opacity:1}}100%{{fill:{COLORS[d["level"]]};opacity:1}}}}')
        css += ['@media(prefers-reduced-motion:reduce){.player{display:none!important}rect{animation:none!important}}']
    p += ['<style>'+''.join(css)+'</style>', '<rect width="1000" height="238" rx="16" fill="#070b14"/>', '<text x="26" y="33" font-size="17" letter-spacing="2" fill="#a88af5">CONTRIBUTION ARCADE</text>', f'<text x="974" y="33" text-anchor="end" font-size="12" fill="#83cbd8">{total:,} contributions · rolling year</text>']
    previous_month = None
    for col, row, d in cells:
        date = dt.date.fromisoformat(d['date'])
        if date.month != previous_month and row == 0:
            p.append(f'<text x="{26+col*18}" y="64" font-size="10" fill="#8f9bb3">{date.strftime("%b")}</text>')
            previous_month = date.month
        label = f'{d["date"]}: {d["contributionCount"]} contributions'
        p.append(f'<rect class="d{arrivals[d["date"]]}" x="{26+col*18}" y="{77+row*18}" width="12" height="12" rx="3" fill="{COLORS[d["level"]]}"><title>{label}</title></rect>')
    p += ['<g class="player"><circle r="8" fill="#ad83ff" opacity=".25"/><circle r="6.8" fill="#63f4f4"/><path class="mouth" d="M0 0L9 -5L9 5Z" fill="#070b14"/><circle cx="-1" cy="-3.3" r="1" fill="#070b14"/></g>', f'<text x="26" y="221" font-size="11" fill="#8f9bb3">{days[0]["date"]} to {days[-1]["date"]} · GitHub contribution data · refreshed every 12 hours</text>', '</svg>']
    return ''.join(p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--public-html', help='Import an official GitHub contribution calendar HTML file for a local preview')
    args = parser.parse_args()
    days = fetch_calendar(args.public_html)
    outputs = {'digital-rain.svg':header(), 'digital-rain-static.svg':header(False), 'contribution-arcade.svg':contribution_svg(days), 'contribution-arcade-static.svg':contribution_svg(days, False), 'contributions.json':json.dumps({'user':'WallfacerX', 'source':'https://github.com/WallfacerX', 'days':days}, indent=2)+'\n'}
    # Validate the entire response before replacing any previous good assets.
    ASSETS.mkdir(exist_ok=True)
    for name, content in outputs.items():
        (ASSETS/name).write_text(content)
    print(f'Generated animations from {len(days)} verified dates, {sum(d["contributionCount"] for d in days)} contributions')

if __name__ == '__main__':
    main()
