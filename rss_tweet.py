#!/usr/bin/env python3
"""
RSS News Tweet for @rajaji2
Reads top DevOps/Cloud blog RSS feeds
Claude writes a commentary tweet about the latest article
Posts once daily via GitHub Actions
Tracks posted URLs to avoid duplicates
"""

import os
import json
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import tweepy
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# ── Credentials ───────────────────────────────────────────────────────────────
X_API_KEY       = os.environ["X_API_KEY"]
X_API_SECRET    = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN  = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]
CLAUDE_API_KEY  = os.environ["CLAUDE_API_KEY"]

POSTED_FILE = "rss_posted.json"

# ── RSS feeds — top DevOps / Cloud / CNCF blogs ───────────────────────────────
RSS_FEEDS = [
    {
        "name": "AWS Blog",
        "url":  "https://aws.amazon.com/blogs/devops/feed/",
        "tag":  "#AWS #DevOps",
    },
    {
        "name": "Kubernetes Blog",
        "url":  "https://kubernetes.io/feed.xml",
        "tag":  "#Kubernetes #CloudNative",
    },
    {
        "name": "HashiCorp Blog",
        "url":  "https://www.hashicorp.com/blog/feed.xml",
        "tag":  "#Terraform #HashiCorp",
    },
    {
        "name": "GitHub Blog (Engineering)",
        "url":  "https://github.blog/engineering.atom",
        "tag":  "#GitHub #DevOps",
    },
    {
        "name": "CNCF Blog",
        "url":  "https://www.cncf.io/blog/feed/",
        "tag":  "#CNCF #CloudNative",
    },
    {
        "name": "Docker Blog",
        "url":  "https://www.docker.com/blog/feed/",
        "tag":  "#Docker #Containers",
    },
    {
        "name": "GitLab Blog",
        "url":  "https://about.gitlab.com/atom.xml",
        "tag":  "#GitLab #CICD",
    },
    {
        "name": "Grafana Blog",
        "url":  "https://grafana.com/blog/index.xml",
        "tag":  "#Grafana #Observability",
    },
    {
        "name": "The New Stack",
        "url":  "https://thenewstack.io/feed/",
        "tag":  "#DevOps #CloudNative",
    },
    {
        "name": "DevOps.com",
        "url":  "https://devops.com/feed/",
        "tag":  "#DevOps",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RSSReader/1.0)"
}


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def load_posted() -> set:
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE) as f:
            data = json.load(f)
            return set(data.get("urls", []))
    return set()


def save_posted(urls: set):
    recent = list(urls)[-500:]
    with open(POSTED_FILE, "w") as f:
        json.dump({"urls": recent, "updated": datetime.utcnow().isoformat()}, f, indent=2)


def fetch_feed(feed: dict) -> list:
    """Fetch RSS/Atom feed, return list of {title, url, summary, published}."""
    try:
        req = urllib.request.Request(feed["url"], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
    except Exception as e:
        print(f"   ⚠️  Could not fetch {feed['name']}: {e}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"   ⚠️  Could not parse {feed['name']}: {e}")
        return []

    ns = {
        "atom":    "http://www.w3.org/2005/Atom",
        "content": "http://purl.org/rss/1.0/modules/content/",
    }

    items = []

    # ── Atom feed ─────────────────────────────────────────────────────────────
    if root.tag == "{http://www.w3.org/2005/Atom}feed" or "feed" in root.tag:
        for entry in root.findall("atom:entry", ns):
            title   = (entry.findtext("atom:title", namespaces=ns) or "").strip()
            link_el = entry.find("atom:link[@rel='alternate']", ns) or entry.find("atom:link", ns)
            url     = link_el.get("href", "") if link_el is not None else ""
            summary = (entry.findtext("atom:summary", namespaces=ns) or
                       entry.findtext("atom:content", namespaces=ns) or "").strip()[:300]
            pub     = entry.findtext("atom:published", namespaces=ns) or \
                      entry.findtext("atom:updated", namespaces=ns) or ""
            if title and url:
                items.append({"title": title, "url": url, "summary": summary, "published": pub})

    # ── RSS feed ──────────────────────────────────────────────────────────────
    else:
        for item in root.findall(".//item"):
            title   = (item.findtext("title") or "").strip()
            url     = (item.findtext("link") or "").strip()
            summary = (item.findtext("description") or "").strip()[:300]
            pub     = item.findtext("pubDate") or ""
            if title and url:
                items.append({"title": title, "url": url, "summary": summary, "published": pub})

    return items


def parse_date(pub_str: str):
    """Try to parse a date string, return datetime or None."""
    if not pub_str:
        return None
    try:
        return parsedate_to_datetime(pub_str).replace(tzinfo=timezone.utc)
    except Exception:
        pass
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(pub_str[:19], fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    except Exception:
        pass
    return None


def find_fresh_article(posted_urls: set) -> dict | None:
    """
    Go through all feeds, return the most recent unposted article
    published within the last 48 hours.
    """
    cutoff    = datetime.now(timezone.utc) - timedelta(hours=48)
    best      = None
    best_time = None

    for feed in RSS_FEEDS:
        print(f"   Fetching {feed['name']}...")
        articles = fetch_feed(feed)

        for art in articles:
            if art["url"] in posted_urls:
                continue

            pub_dt = parse_date(art["published"])

            # Accept articles without a parseable date (assume fresh)
            if pub_dt and pub_dt < cutoff:
                continue

            score_time = pub_dt or datetime.now(timezone.utc)
            if best is None or score_time > best_time:
                best       = {**art, "feed_name": feed["name"], "feed_tag": feed["tag"]}
                best_time  = score_time

    return best


# ═════════════════════════════════════════════════════════════════════════════
# Claude — generate commentary tweet
# ═════════════════════════════════════════════════════════════════════════════

def generate_tweet(article: dict) -> str:
    prompt = (
        f"You are @rajaji2, a DevOps engineer on X (Twitter) sharing news and commentary.\n"
        f"Write ONE engaging tweet (under 220 chars) about this DevOps/Cloud article.\n\n"
        f"Article title  : {article['title']}\n"
        f"Source         : {article['feed_name']}\n"
        f"Summary        : {article['summary'][:200]}\n\n"
        f"Guidelines:\n"
        f"- Add your own opinion, insight, or 'why this matters' angle\n"
        f"- Don't just restate the title — give a hot take or key takeaway\n"
        f"- Sound like a practising DevOps engineer, not a news bot\n"
        f"- End with these tags: {article['feed_tag']}\n"
        f"- Leave room for the URL (it takes 23 chars on X)\n"
        f"- Under 220 chars (URL will be appended separately)\n\n"
        f"Return ONLY the tweet text. No quotes. No URL. No explanation."
    )

    payload = json.dumps({
        "model":      "claude-sonnet-4-6",
        "max_tokens": 200,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"   ❌ Claude error {e.code}: {e.read().decode()}")
        raise

    return data["content"][0]["text"].strip().strip('"').strip("'")


# ═════════════════════════════════════════════════════════════════════════════
# Post to X
# ═════════════════════════════════════════════════════════════════════════════

def post_tweet(text: str) -> str:
    client = tweepy.Client(
        consumer_key        = X_API_KEY,
        consumer_secret     = X_API_SECRET,
        access_token        = X_ACCESS_TOKEN,
        access_token_secret = X_ACCESS_SECRET,
    )
    resp = client.create_tweet(text=text)
    return resp.data["id"]


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print(f"[{datetime.utcnow().isoformat()}] RSS tweet job starting...")
    posted_urls = load_posted()
    print(f"   Already posted: {len(posted_urls)} articles")

    print("\n📡 Scanning feeds for fresh articles...")
    article = find_fresh_article(posted_urls)

    if not article:
        print("   ℹ️  No fresh unposted articles found in any feed. Done.")
        return

    print(f"\n📰 Found: {article['title']}")
    print(f"   Source : {article['feed_name']}")
    print(f"   URL    : {article['url']}")

    print("\n🤖 Generating commentary with Claude...")
    tweet_text = generate_tweet(article)

    # Append URL (X auto-shortens to 23 chars)
    full_tweet = f"{tweet_text}\n\n{article['url']}"

    # Safety trim
    if len(full_tweet) > 280:
        allowed = 280 - len(article['url']) - 4
        tweet_text = tweet_text[:allowed] + "..."
        full_tweet = f"{tweet_text}\n\n{article['url']}"

    print(f"\nTweet ({len(full_tweet)} chars):\n{full_tweet}\n")

    tweet_id = post_tweet(full_tweet)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")

    posted_urls.add(article["url"])
    save_posted(posted_urls)


if __name__ == "__main__":
    main()
