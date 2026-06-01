#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche
Runs via GitHub Actions 5x daily
AI: Google Gemini 2.0 Flash (FREE tier — no credit card needed)
"""

import os
import json
import tweepy
import urllib.request
from datetime import datetime

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
X_API_KEY        = os.environ["X_API_KEY"]
X_API_SECRET     = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN   = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET  = os.environ["X_ACCESS_SECRET"]
GEMINI_API_KEY   = os.environ["GEMINI_API_KEY"]

# ── Tweet slot passed from GitHub Actions (0–4) ───────────────────────────────
SLOT = int(os.environ.get("TWEET_SLOT", "0"))

# ── DevOps project of the day (rotates by weekday) ───────────────────────────
PROJECTS = [
    {"name": "GitHub Actions CI Pipeline",  "stack": "GitHub Actions + Docker",    "tags": "#GitHubActions #CICD #DevOps"},
    {"name": "Terraform AWS EC2 Setup",     "stack": "Terraform + AWS",             "tags": "#Terraform #AWS #IaC"},
    {"name": "K8s Zero-Downtime Deploy",    "stack": "Kubernetes + Helm",           "tags": "#Kubernetes #Helm #CloudNative"},
    {"name": "Docker Multi-Stage Build",    "stack": "Docker",                      "tags": "#Docker #DevOps #Containers"},
    {"name": "Prometheus + Grafana Stack",  "stack": "Docker Compose + Prometheus", "tags": "#Monitoring #Grafana #Observability"},
    {"name": "ArgoCD GitOps Workflow",      "stack": "ArgoCD + Kubernetes",         "tags": "#GitOps #ArgoCD #CICD"},
    {"name": "Nginx Reverse Proxy",         "stack": "Nginx + Docker",              "tags": "#Nginx #Docker #DevOps"},
]

# ── Tweet type prompts ────────────────────────────────────────────────────────
TWEET_TYPES = [
    {
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

# ── Rotating topics ───────────────────────────────────────────────────────────
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
    return PROJECTS[datetime.utcnow().weekday() % len(PROJECTS)]


def get_today_topic():
    return TOPICS[datetime.utcnow().timetuple().tm_yday % len(TOPICS)]


def generate_tweet_gemini(slot: int) -> str:
    project = get_today_project()
    topic   = get_today_topic()
    config  = TWEET_TYPES[slot]

    prompt = config["prompt_template"].format(
        project_name  = project["name"],
        project_stack = project["stack"],
        project_tags  = project["tags"],
        topic         = topic,
    )

    # Gemini 2.0 Flash — free tier, 1500 req/day
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 300, "temperature": 0.9},
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    tweet = data["candidates"][0]["content"]["parts"][0]["text"].strip().strip('"').strip("'")
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
    label = TWEET_TYPES[SLOT]["label"]
    print(f"[{datetime.utcnow().isoformat()}] Slot {SLOT} — {label}")

    tweet_text = generate_tweet_gemini(SLOT)
    print(f"Generated ({len(tweet_text)} chars):\n{tweet_text}\n")

    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."
        print("⚠️  Truncated to 280 chars")

    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
