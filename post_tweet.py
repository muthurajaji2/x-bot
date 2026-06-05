#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche
6 AI-generated tweets/day via Claude API
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

# ── 6 tweet slot prompts ──────────────────────────────────────────────────────
SLOTS = [
    {
        "label": "Project Post",
        "prompt": """You are a DevOps educator tweeting as @rajaji2.
Write ONE tweet about automating a specific DevOps task using a script or tool.
Pick ONE unique topic from: PowerShell automation, Bash scripting, Python DevOps scripts,
Docker setup automation, Kubernetes manifest generation, Terraform provisioning,
GitHub Actions pipeline, CI/CD deployment script, Nginx config automation,
AWS CLI automation, Ansible playbook, Helm chart deployment, Linux cron automation,
Git hooks automation, SonarQube integration, ArgoCD GitOps setup.

STRICT FORMAT - follow this EXACTLY:
<Action verb> <Tool/Topic> like a DevOps Engineer!

✅ <feature 1>
✅ <feature 2>
✅ <feature 3>
✅ <feature 4>
✅ <feature 5>

#<tag1> #<tag2> #<tag3> #<tag4> #<tag5> #<tag6> #<tag7> #<tag8>

EXAMPLE OUTPUT:
Automate MSI Installation using PowerShell like a DevOps Engineer!

✅ Silent Installation
✅ Error Handling
✅ Logging
✅ Exit Code Validation
✅ Enterprise Deployment Ready

#MSI #Automation #DevOps #WindowsAdmin #Scripting #SysAdmin #AzureDevOps #Jenkins

Today: {date}. Pick a DIFFERENT topic from the example. Return ONLY the tweet. No quotes. No extra text.""",
    },
    {
        "label": "Poll",
        "prompt": """You are a DevOps community builder tweeting as @rajaji2.
Write ONE poll tweet for DevOps engineers.

STRICT FORMAT:
<Engaging question about a DevOps tool/practice?>

🔵 <Option A>
🟢 <Option B>
🟡 <Option C>
🔴 <Option D>

#<tag1> #<tag2> #<tag3> #<tag4>

Topics: CI/CD tools, container orchestration, IaC tools, monitoring stacks, cloud providers, scripting languages.
Today: {date}. Return ONLY the tweet. No quotes. No explanation.""",
    },
    {
        "label": "Relatable Meme",
        "prompt": """You are a DevOps/SRE engineer venting on X as @rajaji2.
Write ONE funny relatable tweet about DevOps/SRE/Cloud life.

Use Style B format:
Me: <action>
<Tool/System>: <unexpected response>
Me: <reaction>

OR Style C:
5 stages of <DevOps situation>:
1. <stage>
2. <stage>
3. <stage>
4. <stage>
5. <stage>

Topics: on-call at 3am, terraform destroy, YAML indentation, pipeline failing on Friday,
'works on my machine', kubectl debugging, AWS bill shock, Jenkins flaky builds.
End with #DevOps #SRE or similar.
Today: {date}. Return ONLY the tweet. No quotes. No explanation.""",
    },
    {
        "label": "Career Tip",
        "prompt": """You are a senior DevOps engineer mentoring others as @rajaji2.
Write ONE career tip tweet for DevOps engineers.

STRICT FORMAT:
<Bold career tip title> 🎯

✔️ <specific action or skill>
✔️ <specific action or skill>
✔️ <specific action or skill>
✔️ <specific action or skill>

#<tag1> #<tag2> #<tag3> #<tag4> #<tag5>

Topics: CKA/CKS/AWS certifications, GitHub portfolio, open source contributions,
resume tips, salary negotiation, learning roadmap, side projects, DevOps roadmap 2025.
Today: {date}. Return ONLY the tweet. No quotes. No explanation.""",
    },
    {
        "label": "Motivational",
        "prompt": """You are a DevOps engineer motivating others as @rajaji2.
Write ONE motivational tweet for DevOps/Cloud engineers.

STRICT FORMAT:
<Powerful opening line — a bold statement or challenge>

💪 <action/mindset point 1>
💪 <action/mindset point 2>
💪 <action/mindset point 3>

🔥 <closing motivational line>

#<tag1> #<tag2> #<tag3> #<tag4>

Topics: learning DevOps from scratch, imposter syndrome, first DevOps job,
building in public, never stop learning, open source journey.
Today: {date}. Return ONLY the tweet. No quotes. No explanation.""",
    },
    {
        "label": "Community Question",
        "prompt": """You are a DevOps community builder tweeting as @rajaji2.
Write ONE open-ended question tweet to spark real discussion.

STRICT FORMAT:
<Thought-provoking question to the DevOps community?> 🤔

Drop your answer below 👇

#<tag1> #<tag2> #<tag3> #<tag4>

Topics: real war stories, tool preferences, controversial DevOps opinions,
lessons learned the hard way, what they wish they knew earlier, current stack.
Today: {date}. Return ONLY the tweet. No quotes. No explanation.""",
    },
]


def generate_tweet(slot: int) -> str:
    date_str = datetime.utcnow().strftime("%A %B %d %Y %H:%M UTC")
    prompt   = SLOTS[slot]["prompt"].format(date=date_str)

    payload = json.dumps({
        "model":      "claude-sonnet-4-6",
        "max_tokens": 400,
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

    # Note: These structured tweets can exceed 280 chars — X allows up to 280
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    tweet_id = post_tweet(tweet)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
