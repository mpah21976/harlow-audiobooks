"""To add a book: copy_book.py on the Mac (AngelStudio/feed-copies) makes audio/bookNN/ (chNN.mp3, cover.jpg, chapters.tsv, title.txt); copy it here, run this, commit, push.
Builds feed.xml (one podcast feed for the whole Harlow Home Care Mysteries series) from audio/bookNN/."""
import os, glob, datetime, email.utils, html
BASE = "https://raw.githubusercontent.com/mpah21976/harlow-audiobooks/main/"
TITLES = {1: "Missed Visit", 2: "Change in Condition", 3: "Advance Directive", 4: "Responsible Party", 5: "Homebound",
          6: "Next of Kin", 7: "Incident Report", 8: "Family History", 9: "No Call, No Show", 10: "Safety Plan",
          11: "Readmission", 12: "Emergency Contact", 13: "Living Arrangements", 14: "Self-Administered"}
def dur(path):
    import subprocess
    try:
        out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path],capture_output=True,text=True).stdout
        s = int(float(out)); return f"{s//3600}:{s%3600//60:02d}:{s%60:02d}"
    except Exception: return ""
start = datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc)   # fixed, so the order is always book, then chapter
items = []
for d in sorted(glob.glob("audio/book*")):
    n = int(d[-2:]); t = open(f"{d}/title.txt").read().strip() if os.path.exists(f"{d}/title.txt") else TITLES[n]
    chs = dict(l.split("\t", 1) for l in open(f"{d}/chapters.tsv").read().splitlines() if l)
    for c in sorted(chs, key=int):
        f = f"{d}/ch{int(c):02d}.mp3"
        when = start + datetime.timedelta(days=n * 40 + int(c))
        items.append(f"""  <item>
    <title>{html.escape(f"{t}, Chapter {c}: {chs[c].strip()}")}</title>
    <description>{html.escape(f"Book {n} of the Harlow Home Care Mysteries, by M. P. Asuncion. Read by Ambrose.")}</description>
    <enclosure url="{BASE}{f}" length="{os.path.getsize(f)}" type="audio/mpeg"/>
    <guid isPermaLink="false">harlow-b{n:02d}-c{int(c):02d}</guid>
    <pubDate>{email.utils.format_datetime(when)}</pubDate>
    <itunes:season>{n}</itunes:season>
    <itunes:episode>{c}</itunes:episode>
    <itunes:episodeType>full</itunes:episodeType>
    <itunes:image href="{BASE}{d}/cover.jpg"/>
    <itunes:duration>{dur(f)}</itunes:duration>
  </item>""")
first = sorted(glob.glob("audio/book*"))[0]
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
<channel>
  <title>Harlow Home Care Mysteries</title>
  <link>https://github.com/mpah21976/harlow-audiobooks</link>
  <description>The Harlow Home Care Mysteries by M. P. Asuncion, read by Ambrose. Each book is a season.</description>
  <language>en-us</language>
  <itunes:author>M. P. Asuncion</itunes:author>
  <itunes:type>serial</itunes:type>
  <itunes:explicit>false</itunes:explicit>
  <itunes:block>Yes</itunes:block>
  <itunes:image href="{BASE}{first}/cover.jpg"/>
  <image><url>{BASE}{first}/cover.jpg</url><title>Harlow Home Care Mysteries</title><link>https://github.com/mpah21976/harlow-audiobooks</link></image>
{chr(10).join(items)}
</channel>
</rss>
"""
open("feed.xml", "w").write(feed); print(len(items), "chapters in feed")
