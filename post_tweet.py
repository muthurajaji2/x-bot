#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche
15 AI-generated tweets/day via Claude API
"""

import os
import json
import urllib.request
import urllib.error
import tweepy
from datetime import datetime

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
X_API_KEY       = os.environ["X_API_KEY"]
X_API_SECRET    = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN  = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]
CLAUDE_API_KEY  = os.environ["CLAUDE_API_KEY"]

SLOT = int(os.environ.get("TWEET_SLOT", "0"))

# ── 15 tweet slot prompts ─────────────────────────────────────────────────────
SLOTS = [
    {
        "label": "Project Post",
        "prompt": (
            "You are a DevOps educator tweeting as @rajaji2.\n"
            "Write ONE engaging tweet (under 260 chars) announcing a hands-on DevOps mini project.\n"
            "Pick a unique project using GitHub Actions, Terraform, Kubernetes, Docker, ArgoCD, Prometheus, Grafana, Helm, or AWS.\n"
            "Start with an emoji. End with 2-3 hashtags like #DevOps #CICD #Kubernetes.\n"
            "Today: {date}. Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "DevOps Tip 1",
        "prompt": (
            "You are a senior DevOps engineer sharing tips as @rajaji2.\n"
            "Write ONE practical tip (under 260 chars) with a real command, flag, or config trick.\n"
            "Topics: Kubernetes, Docker, Terraform, GitHub Actions, AWS, Helm.\n"
            "Start with 💡. End with 2-3 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Hot Take",
        "prompt": (
            "You are an opinionated DevOps engineer tweeting as @rajaji2.\n"
            "Write ONE spicy but professional hot take (under 260 chars) about DevOps culture or tools.\n"
            "Start with 'Hot take:' or 'Unpopular opinion:'. End with 1-2 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Poll",
        "prompt": (
            "You are a DevOps community builder tweeting as @rajaji2.\n"
            "Write ONE poll (under 260 chars) for DevOps engineers.\n"
            "Ask a question then list 2-4 options with emoji bullets (🔵 🟢 🟡 🔴).\n"
            "End with #DevOps. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Relatable Meme",
        "prompt": (
            "You are a DevOps/SRE engineer venting on X as @rajaji2.\n"
            "Write ONE funny relatable tweet (under 260 chars) about DevOps/SRE life.\n"
            "Think: on-call, K8s YAML pain, Friday deploys, terraform destroy accidents.\n"
            "End with 1-2 hashtags like #DevOps #SRE. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Tool Spotlight",
        "prompt": (
            "You are a DevOps advocate tweeting as @rajaji2.\n"
            "Write ONE tweet (under 260 chars) spotlighting a useful DevOps/Cloud tool.\n"
            "Mention what it does and one killer feature. Tools: k9s, lazydocker, stern, kubectx, velero, karpenter, etc.\n"
            "Start with an emoji. End with 2-3 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Career Tip",
        "prompt": (
            "You are a senior DevOps engineer mentoring others as @rajaji2.\n"
            "Write ONE career tip (under 260 chars) for aspiring or mid-level DevOps engineers.\n"
            "Topics: certifications, skills, interview tips, open source, building a portfolio.\n"
            "Start with 🎯 or 🚀. End with 2 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Security Tip",
        "prompt": (
            "You are a DevSecOps engineer sharing security tips as @rajaji2.\n"
            "Write ONE security tip (under 260 chars) for DevOps/Cloud engineers.\n"
            "Topics: IAM least privilege, image scanning, secrets management, RBAC, network policies.\n"
            "Start with 🔐 or 🛡️. End with 2-3 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Cloud Cost Tip",
        "prompt": (
            "You are a FinOps engineer sharing cloud cost tips as @rajaji2.\n"
            "Write ONE cloud cost optimization tip (under 260 chars) with a real action engineers can take.\n"
            "Topics: right-sizing, spot instances, reserved instances, S3 lifecycle, unused resources.\n"
            "Start with 💰 or ☁️. End with 2-3 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Learning Resource",
        "prompt": (
            "You are a DevOps educator tweeting as @rajaji2.\n"
            "Write ONE tweet (under 260 chars) recommending a hands-on lab, free course, YouTube channel, or open source project.\n"
            "Be specific — name the resource. Start with 📚 or 🧪. End with 2-3 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "DevOps Tip 2",
        "prompt": (
            "You are a senior DevOps engineer sharing tips as @rajaji2.\n"
            "Write ONE practical tip (under 260 chars) about CI/CD pipelines or automation.\n"
            "Be specific — include a real trick, pattern, or pitfall to avoid.\n"
            "Start with ⚡ or 🔧. End with 2-3 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Kubernetes Tip",
        "prompt": (
            "You are a Kubernetes expert tweeting as @rajaji2.\n"
            "Write ONE Kubernetes-specific tip (under 260 chars) with a real kubectl command, YAML trick, or K8s concept.\n"
            "Start with ☸️. End with 2-3 hashtags like #Kubernetes #K8s #CloudNative. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Terraform / IaC Tip",
        "prompt": (
            "You are a Terraform expert tweeting as @rajaji2.\n"
            "Write ONE Terraform or IaC tip (under 260 chars) with a real command, module pattern, or best practice.\n"
            "Start with 🏗️ or 🟣. End with 2-3 hashtags like #Terraform #IaC #DevOps. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Motivational",
        "prompt": (
            "You are a DevOps engineer motivating others as @rajaji2.\n"
            "Write ONE motivational tweet (under 260 chars) for DevOps/Cloud engineers about growth, persistence, or learning.\n"
            "Make it genuine and specific to the DevOps journey. Start with 💪 or 🌟. End with 1-2 hashtags. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
    {
        "label": "Community Question",
        "prompt": (
            "You are a DevOps community builder tweeting as @rajaji2.\n"
            "Write ONE open-ended question (under 260 chars) to spark discussion among DevOps engineers.\n"
            "Ask about their workflows, preferences, war stories, or opinions — not a poll, just a genuine question.\n"
            "Start with 🤔 or 💬. End with #DevOps. Today: {date}.\n"
            "Return ONLY the tweet. No quotes. No explanation."
        ),
    },
]


def generate_tweet(slot: int) -> str:
    date_str = datetime.utcnow().strftime("%A %B %d %Y %H:%M UTC")
    prompt   = SLOTS[slot]["prompt"].format(date=date_str)

    payload = json.dumps({
        "model":      "claude-sonnet-4-6",
        "max_tokens": 300,
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
        print(f"❌ Claude error {e.code}: {e.read().decode()}")
        raise

    return data["content"][0]["text"].strip().strip('"').strip("'")


def post_tweet(text: str) -> str:
    client = tweepy.Client(
        consumer_key        = X_API_KEY,
        consumer_secret     = X_API_SECRET,
        access_token        = X_ACCESS_TOKEN,
        access_token_secret = X_ACCESS_SECRET,
    )
    resp = client.create_tweet(text=text)
    return resp.data["id"]


def main():
    label = SLOTS[SLOT]["label"]
    print(f"[{datetime.utcnow().isoformat()}] Slot {SLOT} — {label}")
    print("🤖 Generating with Claude...")

    tweet = generate_tweet(SLOT)
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}\n")

    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    tweet_id = post_tweet(tweet)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
