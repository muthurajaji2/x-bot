#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
2 tweets/day via Claude API
Slot 0 — DevOps Article (10:00 AM IST)
Slot 1 — CI/CD Content  (06:00 PM IST)
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

# ─────────────────────────────────────────────────────────────────────────────
# SLOT 0 — DevOps Article topics (40 unique topics, rotates daily)
# ─────────────────────────────────────────────────────────────────────────────
SLOT0_TOPICS = [
    "What is DevOps and why every company needs it in 2025",
    "How Site Reliability Engineering (SRE) is different from DevOps",
    "The 4 DORA metrics every DevOps team should track",
    "What is GitOps and how it changes infrastructure management",
    "How to implement zero-downtime deployments in production",
    "The DevOps engineer roadmap for beginners in 2025",
    "What is Platform Engineering and why it is replacing DevOps teams",
    "How to build a DevOps culture in a traditional IT company",
    "What is FinOps and why cloud cost matters for DevOps engineers",
    "The difference between Continuous Integration and Continuous Delivery",
    "How Kubernetes changed the way we deploy software",
    "What is Infrastructure as Code and why it matters",
    "How to implement DevSecOps in your pipeline",
    "The top 10 DevOps tools every engineer must know in 2025",
    "What is Observability and how it is different from Monitoring",
    "How to reduce MTTR (Mean Time to Recovery) in production",
    "What is Chaos Engineering and how Netflix uses it",
    "How to build a DevOps portfolio that gets you hired",
    "The role of AI and Machine Learning in modern DevOps",
    "What is Service Mesh and when should you use Istio",
    "How to implement blue-green deployments step by step",
    "What is Container Security and how to harden Docker images",
    "How Ansible automates configuration management at scale",
    "What is eBPF and why it is revolutionizing cloud-native observability",
    "How to design a multi-cloud strategy for your organisation",
    "What is Kubernetes Operators and how they extend K8s capabilities",
    "How to implement GitLab CI/CD from scratch",
    "What is Feature Flags and how to use them safely in production",
    "How to migrate from monolith to microservices with zero downtime",
    "What is the CALMS framework in DevOps",
    "How to implement shift-left security in your DevOps pipeline",
    "What is Progressive Delivery and how canary releases work",
    "How HashiCorp Vault manages secrets at enterprise scale",
    "What is OpenTelemetry and how it standardises observability",
    "How to build a self-service developer platform with Backstage",
    "What is Kubernetes RBAC and how to secure your cluster",
    "How to implement automated compliance checks in CI/CD",
    "What is Supply Chain Security in DevOps and how to protect it",
    "How to use Terraform modules for reusable infrastructure",
    "What is AIOps and how AI is transforming IT operations",
]

# ─────────────────────────────────────────────────────────────────────────────
# SLOT 1 — CI/CD topics (40 unique topics, rotates daily)
# ─────────────────────────────────────────────────────────────────────────────
SLOT1_TOPICS = [
    "Build a GitHub Actions CI pipeline for a Python app",
    "Set up GitLab CI/CD with Docker and Kubernetes",
    "Automate Docker image builds and push to ECR using GitHub Actions",
    "Build a Jenkins declarative pipeline from scratch",
    "Set up branch protection rules and required CI checks on GitHub",
    "Automate Terraform plan and apply using GitHub Actions",
    "Build a multi-stage CI pipeline with test, build, and deploy stages",
    "Set up ArgoCD for continuous delivery to Kubernetes",
    "Automate semantic versioning and changelog generation in CI",
    "Build a GitHub Actions matrix to test across multiple Python versions",
    "Set up dependency caching in GitHub Actions to speed up pipelines",
    "Automate Docker vulnerability scanning using Trivy in CI",
    "Build a GitOps pipeline with ArgoCD and GitHub",
    "Set up environment-specific deployments using GitHub Actions environments",
    "Automate Helm chart deployment using GitHub Actions",
    "Build a CircleCI pipeline with parallelism and test splitting",
    "Set up SonarQube code quality gates in your CI pipeline",
    "Automate AWS Lambda deployment using GitHub Actions and SAM",
    "Build a monorepo CI pipeline with GitHub Actions path filters",
    "Set up Slack notifications for CI/CD pipeline success and failure",
    "Automate database migrations in your CI/CD pipeline safely",
    "Build a Jenkins shared library for reusable pipeline code",
    "Set up OIDC authentication between GitHub Actions and AWS",
    "Automate integration tests using Docker Compose in CI",
    "Build a rollback mechanism in your GitHub Actions deployment pipeline",
    "Set up deployment gates and manual approval in GitHub Actions",
    "Automate container image tagging strategy in CI/CD",
    "Build a pipeline to deploy to AWS EKS using GitHub Actions",
    "Set up code coverage reports and thresholds in CI pipeline",
    "Automate secrets rotation in your CI/CD pipeline using Vault",
    "Build a GitLab CI pipeline with review apps for every PR",
    "Set up GitHub Actions self-hosted runners on AWS EC2",
    "Automate infrastructure drift detection using Terraform in CI",
    "Build a canary deployment pipeline using Argo Rollouts",
    "Set up performance testing in your CI pipeline using k6",
    "Automate API contract testing in CI using Pact",
    "Build a GitHub Actions workflow to publish npm packages automatically",
    "Set up Blue-Green deployment pipeline on AWS ECS",
    "Automate security SAST scanning using Semgrep in CI",
    "Build a complete DevSecOps pipeline with scan, sign, and deploy stages",
]


def get_todays_topic(slot: int) -> str:
    day   = datetime.utcnow().timetuple().tm_yday
    pool  = SLOT0_TOPICS if slot == 0 else SLOT1_TOPICS
    # Different starting offsets so slot 0 and slot 1 never pick same index
    offset = 0 if slot == 0 else 19
    index  = (day - 1 + offset) % len(pool)
    return pool[index]


def build_prompt(slot: int, topic: str) -> str:

    if slot == 0:
        # DevOps Article — educational thread-style tweet
        return f"""You are a DevOps educator tweeting as @rajaji2.
Write ONE educational tweet about this DevOps topic: {topic}

STRICT FORMAT:
📖 <catchy article-style headline about {topic}>

<2-3 lines explaining the key concept clearly — what it is, why it matters, one insight>

🔗 Key takeaways:
→ <takeaway 1>
→ <takeaway 2>
→ <takeaway 3>

#<tag1> #<tag2> #<tag3> #<tag4> #<tag5> #<tag6> #<tag7> #<tag8> #<tag9> #<tag10>

EXAMPLE:
📖 What is GitOps and why is everyone talking about it?

GitOps treats your Git repo as the single source of truth for infrastructure. Any change to prod goes through a PR — not a CLI command.

🔗 Key takeaways:
→ Git history = full audit trail of every infra change
→ Rollback = just revert a commit
→ ArgoCD and Flux are the top GitOps tools in 2025

#GitOps #DevOps #Kubernetes #ArgoCD #CloudNative #IaC #Platform #SRE #Automation #CICD

Rules:
- Be specific and educational about "{topic}"
- Write for a DevOps engineer audience
- Always include exactly 10 hashtags — mix broad (#DevOps #Cloud) and specific ones
- Keep total tweet under 280 chars
- Return ONLY the tweet. No quotes. No explanation."""

    else:
        # CI/CD — hands-on checklist tweet
        return f"""You are a CI/CD expert tweeting as @rajaji2.
Write ONE hands-on tweet about this CI/CD topic: {topic}

STRICT FORMAT:
{topic} like a DevOps Engineer!

✅ <specific step or feature 1>
✅ <specific step or feature 2>
✅ <specific step or feature 3>
✅ <specific step or feature 4>
✅ <specific step or feature 5>

#<tag1> #<tag2> #<tag3> #<tag4> #<tag5> #<tag6> #<tag7> #<tag8> #<tag9> #<tag10>

EXAMPLE:
Build a GitHub Actions CI pipeline for a Python app like a DevOps Engineer!

✅ Trigger on push and pull_request to main branch
✅ Set up Python matrix for versions 3.10, 3.11, 3.12
✅ Cache pip dependencies using actions/cache
✅ Run pytest with coverage report
✅ Fail pipeline if coverage drops below 80%

#GitHubActions #CICD #Python #DevOps #Automation #CI #Testing #Pipeline #SRE #Kubernetes

Rules:
- All 5 checkmarks must be specific to "{topic}"
- Always include exactly 10 hashtags — mix broad (#DevOps #Cloud) and specific ones
- Keep total tweet under 280 chars
- Return ONLY the tweet. No quotes. No explanation."""


def generate_tweet(slot: int) -> str:
    topic  = get_todays_topic(slot)
    prompt = build_prompt(slot, topic)

    print(f"   📌 Today's topic for slot {slot}: {topic}")

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
    labels = ["DevOps Article", "CI/CD Content"]
    print(f"[{datetime.utcnow().isoformat()}] Slot {SLOT} — {labels[SLOT]}")
    print("🤖 Generating with Claude...")

    tweet = generate_tweet(SLOT)
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}\n")

    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    tweet_id = post_tweet(tweet)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
