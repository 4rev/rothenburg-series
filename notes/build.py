"""Build the Field Notes pages from notes/entries/*.md.

Stdlib only. Run from anywhere:  python notes/build.py
Writes notes/index.html, notes/<slug>/index.html and notes/feed.xml.

Entry format:
    title: ...
    date: YYYY-MM-DD
    tags: A, B
    summary: one sentence
    ---
    body: paragraphs, - lists, 1. lists, | tables |, ``` code ```, `code`, **bold**, [text](url)
"""
import html
import pathlib
import re
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
SITE = "https://4rev.github.io/rothenburg-series"
BASE = SITE + "/notes/"
WALL = "https://www.fab.com/listings/aca56f80-cb23-4aca-8c51-ba31bc07070e"
DOCS = SITE + "/wallsystem/"
STORE = "https://www.fab.com/sellers/Pierogi3"
BYLINE = ("Written by Claude (an AI) from the build log of Medieval Wall Generator. "
          "Each note comes from a real bug we hit and fixed.")


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    return t


def render(md):
    out, lines, i = [], md.strip("\n").split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class=tw><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        elif re.match(r"(- |\d+\. )", ln):
            tag = "ol" if ln[0].isdigit() else "ul"
            items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append("<li>" + inline(re.sub(r"^(- |\d+\. )", "", lines[i])) + "</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
        elif not ln.strip():
            i += 1
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(```|\||- |\d+\. )", lines[i]):
                para.append(lines[i])
                i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def load():
    entries = []
    for f in sorted(HERE.glob("entries/*.md")):
        head, body = f.read_text(encoding="utf-8").split("\n---\n", 1)
        meta = dict(l.split(": ", 1) for l in head.strip().split("\n"))
        meta["slug"] = f.stem[11:]
        meta["body"] = render(body)
        meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        entries.append(meta)
    return sorted(entries, key=lambda e: e["date"], reverse=True)


CSS = """
:root{--paper:#F1F1EE;--ink:#1D2325;--muted:#59646A;--rule:#BCC1BE;--gold:#C79E56;--teal:#1F6455;
  --panel:#E5E6E1;--code:#20262A;--card:#fff;
  --sans:'Archivo Narrow','Arial Narrow',Arial,sans-serif;--serif:'EB Garamond',Georgia,serif}
@media (prefers-color-scheme:dark){:root{--paper:#15191B;--ink:#DEE3DF;--muted:#939E9C;--rule:#333B3D;
  --gold:#C79E56;--teal:#6CBCA6;--panel:#1D2325;--code:#0E1112;--card:#1D2325}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:18px;
  line-height:1.62;-webkit-text-size-adjust:100%}
.masthead{border-bottom:1px solid var(--rule)}
.masthead .in{max-width:780px;margin:0 auto;padding:18px 16px;display:flex;align-items:baseline;
  gap:16px;flex-wrap:wrap}
.masthead a.home{font-family:var(--sans);text-transform:uppercase;letter-spacing:.14em;font-size:12px;
  color:var(--muted);text-decoration:none}
.masthead a.home:hover{color:var(--teal)}
.masthead a.buy{margin-left:auto;font-family:var(--sans);text-transform:uppercase;letter-spacing:.12em;
  font-size:11px;font-weight:700;text-decoration:none;color:var(--paper);background:var(--teal);
  padding:7px 13px;border-radius:2px;white-space:nowrap}
main{max-width:780px;margin:0 auto;padding:34px 16px 72px}
.eyebrow{font-family:var(--sans);text-transform:uppercase;letter-spacing:.16em;font-size:11px;
  color:var(--muted);margin:0}
h1{font-family:var(--sans);font-weight:700;font-size:38px;line-height:1.1;margin:.2em 0 .3em}
h2{font-family:var(--sans);font-weight:600;font-size:22px;line-height:1.25;margin:0 0 .25em}
h2 a{color:var(--ink);text-decoration:none}h2 a:hover{color:var(--teal)}
.lede{font-size:20px;color:var(--muted);margin:.4em 0 1.2em}
.by{font-family:var(--sans);font-size:13px;color:var(--muted);border-left:3px solid var(--gold);
  padding:2px 0 2px 12px;margin:1em 0 2em}
a{color:var(--teal)}strong{font-weight:600}
code{font-family:ui-monospace,'Cascadia Mono',Consolas,monospace;font-size:.84em;background:var(--panel);
  border:1px solid var(--rule);border-radius:3px;padding:.05em .35em;overflow-wrap:anywhere}
pre{background:var(--code);color:#DEE3DF;padding:14px 16px;border-radius:4px;overflow-x:auto;
  font-size:14px;line-height:1.55;margin:1.2em 0}
pre code{background:none;border:0;padding:0;color:inherit;font-size:inherit;overflow-wrap:normal}
.tw{overflow-x:auto;margin:1.3em 0;border:1px solid var(--rule);border-radius:4px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:15.5px;font-family:var(--sans)}
th,td{text-align:left;padding:9px 13px;border-bottom:1px solid var(--rule);vertical-align:top}
thead th{background:var(--panel);font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted)}
tbody tr:last-child td{border-bottom:0}
.tags{font-family:var(--sans);font-size:12px;color:var(--muted);letter-spacing:.06em}
.tags span{border:1px solid var(--rule);border-radius:2px;padding:1px 7px;margin-right:6px}
ol.list{list-style:none;padding:0;margin:2em 0}
ol.list li{border-top:1px solid var(--rule);padding:22px 0}
ol.list p{margin:.3em 0 .5em}
.cta{margin-top:3em;border:1px solid var(--rule);background:var(--card);border-radius:4px;padding:18px 20px}
.cta p{margin:.2em 0 .8em}
.cta a.btn{display:inline-block;font-family:var(--sans);text-transform:uppercase;letter-spacing:.12em;
  font-size:12px;font-weight:700;text-decoration:none;color:var(--paper);background:var(--teal);
  padding:8px 14px;border-radius:2px;margin-right:12px}
footer{border-top:1px solid var(--rule);padding:22px 16px 48px;font-family:var(--sans);font-size:12.5px;color:var(--muted)}
footer .in{max-width:780px;margin:0 auto;display:flex;gap:18px;flex-wrap:wrap}
footer a{color:var(--muted)}
@media(max-width:600px){h1{font-size:30px}body{font-size:17px}}
"""


def page(title, desc, url, body):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang=en>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{t} | Field Notes</title>
<meta name=description content="{d}">
<link rel=canonical href="{url}">
<link rel=alternate type="application/rss+xml" title="Field Notes" href="{BASE}feed.xml">
<meta property="og:type" content="article">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel=preconnect href="https://fonts.googleapis.com">
<link rel=preconnect href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel=stylesheet>
<style>{CSS}</style>
</head>
<body>
<header class=masthead><div class=in>
  <a class=home href="{SITE}/">&#8592; The Rothenburg Series</a>
  <a class=home href="{BASE}">Field Notes</a>
  <a class=buy href="{WALL}">Medieval Wall Generator &middot; Fab</a>
</div></header>
<main>
{body}
</main>
<footer><div class=in>
  <span>&copy; 2026 Pierogi3</span>
  <a href="{BASE}">All field notes</a>
  <a href="{BASE}feed.xml">RSS</a>
  <a href="{DOCS}">Wall Generator manual</a>
  <a href="{STORE}">Fab store</a>
</div></footer>
</body>
</html>
"""


def tags(e):
    return '<div class=tags>' + "".join(f"<span>{html.escape(t)}</span>" for t in e["tags"]) + "</div>"


def main():
    entries = load()
    cta = f"""<div class=cta>
<p class=eyebrow>Where this came from</p>
<p>We hit this while building <strong>Medieval Wall Generator</strong>, a UE 5.8 plugin: draw a
spline, bake a destructible castle wall that AI can walk and guard.</p>
<a class=btn href="{WALL}">See it on Fab</a><a href="{DOCS}">Read the manual</a>
</div>"""
    for e in entries:
        url = BASE + e["slug"] + "/"
        body = (f'<p class=eyebrow>Field note &middot; {e["date"]}</p>\n<h1>{html.escape(e["title"])}</h1>\n'
                f'<p class=lede>{html.escape(e["summary"])}</p>\n{tags(e)}\n<p class=by>{BYLINE}</p>\n'
                f'{e["body"]}\n{cta}')
        out = HERE / e["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page(e["title"], e["summary"], url, body), encoding="utf-8")

    items = "".join(
        f'<li><p class=eyebrow>{e["date"]}</p><h2><a href="{e["slug"]}/">{html.escape(e["title"])}</a></h2>'
        f'<p>{html.escape(e["summary"])}</p>{tags(e)}</li>' for e in entries)
    idx = (f'<p class=eyebrow>Field Notes</p>\n<h1>Unreal Engine traps, measured</h1>\n'
           f'<p class=lede>Short notes on UE 5.8 bugs we hit while building a castle-wall plugin. '
           f'Each one has the cause, the fix and how we proved it.</p>\n<p class=by>{BYLINE}</p>\n'
           f'<ol class=list>{items}</ol>\n{cta}')
    (HERE / "index.html").write_text(page("Field Notes", "Unreal Engine 5 traps we hit while building "
        "Medieval Wall Generator, each with cause, fix and proof.", BASE, idx), encoding="utf-8")

    def rfc822(d):
        return datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y 09:00:00 +0000")
    rss = "".join(
        f"<item><title>{html.escape(e['title'])}</title><link>{BASE}{e['slug']}/</link>"
        f"<guid>{BASE}{e['slug']}/</guid><pubDate>{rfc822(e['date'])}</pubDate>"
        f"<description>{html.escape(e['summary'])}</description></item>" for e in entries)
    (HERE / "feed.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel>'
        f"<title>Field Notes - Medieval Wall Generator</title><link>{BASE}</link>"
        "<description>Unreal Engine 5 traps, measured.</description>" + rss + "</channel></rss>\n",
        encoding="utf-8")
    print(f"built {len(entries)} notes")


if __name__ == "__main__":
    main()
