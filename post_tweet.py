#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche — 5 tweets/day
AI: Claude API (Anthropic) — fresh unique tweet generated every run
"""

import os
import json
import tweepy
import urllib.request
import urllib.error
from datetime import datetime

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
X_API_KEY        = os.environ["X_API_KEY"]
X_API_SECRET     = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN   = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET  = os.environ["X_ACCESS_SECRET"]
CLAUDE_API_KEY   = os.environ["CLAUDE_API_KEY"]

# ── Tweet slot (0–4) passed by GitHub Actions ─────────────────────────────────
SLOT = int(os.environ.get("TWEET_SLOT", "0"))

# ── Slot config ───────────────────────────────────────────────────────────────
SLOTS = [
    {
        "label": "Project Post",
        "time":  "8:00 AM IST",
        "prompt": (
            "You are a DevOps educator tweeting as @rajaji2 on X (Twitter).\n"
            "Write ONE engaging tweet (strictly under 260 characters) announcing a hands-on DevOps mini project.\n"
            "Pick a unique project idea involving: GitHub Actions, Terraform, Kubernetes, Docker, ArgoCD, Prometheus, Grafana, Helm, AWS, or similar DevOps tools.\n"
            "Format: start with an emoji, say what the reader will BUILD or LEARN, end with 2-3 hashtags like #DevOps #CICD #Kubernetes.\n"
            "Today's date: {date}. Make it feel fresh and specific.\n"
            "Return ONLY the tweet text. No quotes. No explanation. No preamble."
        ),
    },
    {
        "label": "DevOps Tip",
        "time":  "11:00 AM IST",
        "prompt": (
            "You are a senior DevOps engineer sharing daily tips as @rajaji2 on X (Twitter).\n"
            "Write ONE practical technical tip (strictly under 260 characters) for DevOps/Cloud engineers.\n"
            "Be specific — include a real command, flag, config trick, or tool name.\n"
            "Topics: Kubernetes, Docker, Terraform, GitHub Actions, AWS, CI/CD, Helm, monitoring, security.\n"
            "Start with 💡. End with 2-3 hashtags. Today's date: {date}.\n"
            "Return ONLY the tweet text. No quotes. No explanation. No preamble."
        ),
    },
    {
        "label": "Hot Take",
        "time":  "2:00 PM IST",
        "prompt": (
            "You are an opinionated DevOps engineer tweeting as @rajaji2 on X (Twitter).\n"
            "Write ONE spicy but professional hot take (strictly under 260 characters) about DevOps culture, tools, or industry practices.\n"
            "It should provoke thought or debate. Start with 'Hot take:' or 'Unpopular opinion:'.\n"
            "End with 1-2 relevant hashtags. Today's date: {date}.\n"
            "Return ONLY the tweet text. No quotes. No explanation. No preamble."
        ),
    },
    {
        "label": "Poll / Question",
        "time":  "5:00 PM IST",
        "prompt": (
            "You are a DevOps community builder tweeting as @rajaji2 on X (Twitter).\n"
            "Write ONE engaging community poll or question (strictly under 260 characters) for DevOps engineers.\n"
            "Format: ask a question, then list 2-4 answer options with emoji bullets (🔵 🟢 🟡 🔴).\n"
            "End with a relevant hashtag like #DevOps. Today's date: {date}.\n"
            "Return ONLY the tweet text. No quotes. No explanation. No preamble."
        ),
    },
    {
        "label": "Relatable Meme",
        "time":  "9:00 PM IST",
        "prompt": (
            "You are a DevOps/SRE engineer venting on X (Twitter) as @rajaji2.\n"
            "Write ONE funny, relatable tweet (strictly under 260 characters) about the DevOps/SRE/cloud engineer life.\n"
            "Think: on-call nightmares, K8s YAML pain, Friday deploys, terraform destroy accidents, 'works on my machine'.\n"
            "End with 1-2 hashtags like #DevOps #SRE. Today's date: {date}.\n"
            "Return ONLY the tweet text. No quotes. No explanation. No preamble."
        ),
    },
]


def generate_tweet(slot: int) -> str:
    config = SLOTS[slot]
    now    = datetime.utcnow()
    date_str = now.strftime("%A, %B %d %Y %H:%M UTC")

    prompt = config["prompt"].format(date=date_str)

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}],
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
        body = e.read().decode()
        print(f"❌ Claude API error {e.code}: {body}")
        raise

    tweet = data["content"][0]["text"].strip().strip('"').strip("'")
    return tweet


def post_tweet(text: str) -> str:
    client = tweepy.Client(
        consumer_key        = X_API_KEY,
        consumer_secret     = X_API_SECRET,
        access_token        = X_ACCESS_TOKEN,
        access_token_secret = X_ACCESS_SECRET,
    )
    response = client.create_tweet(text=text)
    return response.data["id"]


def main():
    config = SLOTS[SLOT]
    print(f"[{datetime.utcnow().isoformat()}] Slot {SLOT} — {config['label']} ({config['time']})")
    print("🤖 Asking Claude to generate tweet...")

    tweet_text = generate_tweet(SLOT)
    print(f"\nGenerated tweet ({len(tweet_text)} chars):\n{tweet_text}\n")

    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."
        print("⚠️  Truncated to 280 chars")

    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
