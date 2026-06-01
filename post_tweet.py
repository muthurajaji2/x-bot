#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche
Runs via GitHub Actions 5x daily
"""

import os
import sys
import json
import tweepy
import anthropic
from datetime import datetime

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
X_API_KEY            = os.environ["X_API_KEY"]
X_API_SECRET         = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN       = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET      = os.environ["X_ACCESS_SECRET"]
CLAUDE_API_KEY       = os.environ["CLAUDE_API_KEY"]

# ── Tweet slot passed from GitHub Actions (0–4) ───────────────────────────────
SLOT = int(os.environ.get("TWEET_SLOT", "0"))

# ── DevOps project of the day (rotates by weekday) ───────────────────────────
PROJECTS = [
    {"name": "GitHub Actions CI Pipeline",   "stack": "GitHub Actions + Docker",   "tags": "#GitHubActions #CICD #DevOps"},
    {"name": "Terraform AWS EC2 Setup",      "stack": "Terraform + AWS",            "tags": "#Terraform #AWS #IaC"},
    {"name": "K8s Zero-Downtime Deploy",     "stack": "Kubernetes + Helm",          "tags": "#Kubernetes #Helm #CloudNative"},
    {"name": "Docker Multi-Stage Build",     "stack": "Docker",                     "tags": "#Docker #DevOps #Containers"},
    {"name": "Prometheus + Grafana Stack",   "stack": "Docker Compose + Prometheus","tags": "#Monitoring #Grafana #Observability"},
    {"name": "ArgoCD GitOps Workflow",       "stack": "ArgoCD + Kubernetes",        "tags": "#GitOps #ArgoCD #CICD"},
    {"name": "Nginx Reverse Proxy",          "stack": "Nginx + Docker",             "tags": "#Nginx #Docker #DevOps"},
]

# ── Tweet type config ─────────────────────────────────────────────────────────
TWEET_TYPES = [
    {
        "slot": 0,
        "time": "08:00 UTC",
        "label": "Project Post",
        "prompt_template": (
            "You are a DevOps educator on X (Twitter) for account @rajaji2.\n"
            "Write a single engaging tweet (under 270 chars) announcing today's hands-on project:\n"
            "  Project: {project_name}\n"
            "  Stack:   {project_stack}\n"
            "Make it exciting. Tell readers what they will BUILD or LEARN. "
            "End with these hashtags: {project_tags}\n"
            "Return ONLY the tweet text. No quotes. No explanation."
        ),
    },
    {
        "slot": 1,
        "time": "11:00 UTC",
        "label": "DevOps Tip",
        "prompt_template": (
            "You are a senior DevOps engineer sharing tips on X (Twitter) as @rajaji2.\n"
            "Write ONE practical, technical tip (under 270 chars) about: {topic}\n"
            "Be specific — mention a real command, tool, or config trick. "
            "Add 2-3 relevant hashtags like #DevOps #Kubernetes #AWS #CICD #Terraform.\n"
            "Return ONLY the tweet text. No quotes. No explanation."
        ),
    },
    {
        "slot": 2,
        "time": "14:00 UTC",
        "label": "Hot Take",
        "prompt_template": (
            "You are an opinionated DevOps engineer on X (Twitter) as @rajaji2.\n"
            "Write a spicy but professional hot take (under 270 chars) about DevOps culture, "
            "tooling choices, or industry practices. It should spark debate.\n"
            "Topic area: {topic}\n"
            "Add 1-2 hashtags. Return ONLY the tweet text. No quotes. No explanation."
        ),
    },
    {
        "slot": 3,
        "time": "17:00 UTC",
        "label": "Poll / Question",
        "prompt_template": (
            "You are a DevOps community builder on X (Twitter) as @rajaji2.\n"
            "Write an engaging poll or open question (under 270 chars) for the DevOps community.\n"
            "Topic: {topic}\n"
            "Format: Ask the question, then list 2-4 emoji-bulleted answer options.\n"
            "Add #DevOps or relevant hashtag. Return ONLY the tweet text. No quotes."
        ),
    },
    {
        "slot": 4,
        "time": "21:00 UTC",
        "label": "Relatable Meme",
        "prompt_template": (
            "You are a DevOps/SRE engineer venting on X (Twitter) as @rajaji2.\n"
            "Write a funny, relatable tweet (under 270 chars) about the DevOps/SRE/cloud engineer life.\n"
            "Think: on-call nightmares, Kubernetes YAML pain, pipelines breaking on Friday, "
            "terraform destroy accidents, 'works on my machine', etc.\n"
            "Add 1-2 hashtags like #DevOps #SRE. Return ONLY the tweet text. No quotes."
        ),
    },
]

# ── Rotating topic list ───────────────────────────────────────────────────────
TOPICS = [
    "Kubernetes resource limits and requests",
    "GitHub Actions caching strategies",
    "Terraform state management best practices",
    "Docker layer caching optimization",
    "Helm chart versioning",
    "AWS IAM least privilege",
    "ArgoCD sync policies",
    "Prometheus alerting rules",
    "Zero-downtime Kubernetes deployments",
    "CI/CD pipeline security scanning",
    "Multi-stage Docker builds",
    "Kubernetes RBAC configuration",
    "Terraform modules and reusability",
    "GitHub Actions matrix builds",
    "Grafana dashboard best practices",
]


def get_today_project():
    day = datetime.utcnow().weekday()  # 0=Mon … 6=Sun
    return PROJECTS[day % len(PROJECTS)]


def get_today_topic():
    day = datetime.utcnow().timetuple().tm_yday  # day of year
    return TOPICS[day % len(TOPICS)]


def generate_tweet(slot: int) -> str:
    project = get_today_project()
    topic   = get_today_topic()
    config  = TWEET_TYPES[slot]

    prompt = config["prompt_template"].format(
        project_name  = project["name"],
        project_stack = project["stack"],
        project_tags  = project["tags"],
        topic         = topic,
    )

    claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    response = claude.messages.create(
        model      = "claude-sonnet-4-20250514",
        max_tokens = 300,
        messages   = [{"role": "user", "content": prompt}],
    )

    tweet = response.content[0].text.strip().strip('"').strip("'")
    return tweet


def post_tweet(text: str):
    client = tweepy.Client(
        consumer_key        = X_API_KEY,
        consumer_secret     = X_API_SECRET,
        access_token        = X_ACCESS_TOKEN,
        access_token_secret = X_ACCESS_SECRET,
    )
    response = client.create_tweet(text=text)
    return response.data["id"]


def main():
    print(f"[{datetime.utcnow().isoformat()}] Running slot {SLOT} — {TWEET_TYPES[SLOT]['label']}")

    tweet_text = generate_tweet(SLOT)
    print(f"Generated tweet ({len(tweet_text)} chars):\n{tweet_text}\n")

    if len(tweet_text) > 280:
        print("⚠️  Tweet too long, truncating...")
        tweet_text = tweet_text[:277] + "..."

    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted successfully! Tweet ID: {tweet_id}")
    print(f"   View at: https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
