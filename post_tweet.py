#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche
6 AI-generated tweets/day via Claude API
FIXED: Each slot has its OWN topic list — no repeated topics ever
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
# TOPIC LISTS — one list per slot
# Topic rotates daily using day-of-year so each day is different
# 40 topics = no repeat for 40 days
# ─────────────────────────────────────────────────────────────────────────────

# Slot 0 — Project Post topics (40 unique DevOps automation topics)
SLOT0_TOPICS = [
    "Automate MSI Installation using PowerShell",
    "Build a CI Pipeline using GitHub Actions",
    "Deploy Nginx using Docker Compose",
    "Automate AWS EC2 provisioning using Terraform",
    "Set up Kubernetes RBAC using kubectl",
    "Automate Docker Image Builds using Jenkins",
    "Deploy a Flask App to AWS ECS using Terraform",
    "Monitor Linux Servers using Prometheus and Node Exporter",
    "Automate SSL Certificate Renewal using Certbot and Cron",
    "Build a Multi-Stage Docker Build for a Node.js App",
    "Set up ArgoCD GitOps Pipeline on Kubernetes",
    "Automate Database Backups to AWS S3 using Bash",
    "Deploy Microservices using Helm Charts",
    "Build a Zero-Downtime Deployment Pipeline using GitHub Actions",
    "Automate Log Rotation using Bash and Cron",
    "Set up Grafana Dashboards using Docker Compose",
    "Automate Kubernetes Namespace Creation using Python",
    "Build a Self-Healing Infrastructure using Ansible",
    "Deploy Redis Cluster using Kubernetes StatefulSets",
    "Automate Terraform State Management using S3 and DynamoDB",
    "Set up Distributed Tracing using Jaeger on Kubernetes",
    "Automate Docker Container Health Checks using Bash",
    "Build a GitLab CI/CD Pipeline from Scratch",
    "Deploy HashiCorp Vault on Kubernetes",
    "Automate AWS IAM User Creation using Python Boto3",
    "Set up Fluentd Log Aggregation on Kubernetes",
    "Build a Custom Prometheus Exporter using Python",
    "Automate Linux User Management using Ansible Playbook",
    "Deploy a Static Website to AWS S3 with CloudFront using Terraform",
    "Set up Kubernetes Horizontal Pod Autoscaler (HPA)",
    "Automate Docker Registry Cleanup using Shell Script",
    "Build a Canary Deployment Pipeline using Argo Rollouts",
    "Automate AWS Lambda Deployment using GitHub Actions",
    "Set up Network Policies in Kubernetes",
    "Automate SonarQube Code Quality Checks in CI/CD",
    "Build a Kubernetes Operator using Python",
    "Automate Secrets Management using HashiCorp Vault and Terraform",
    "Deploy Kafka on Kubernetes using Helm",
    "Automate Kubernetes Cluster Upgrades using kubeadm",
    "Set up Istio Service Mesh on Kubernetes",
]

# Slot 1 — Poll topics (40 unique DevOps community questions)
SLOT1_TOPICS = [
    "CI/CD tool preference: Jenkins vs GitHub Actions vs GitLab CI vs CircleCI",
    "Container orchestration: Kubernetes vs Docker Swarm vs Nomad vs ECS",
    "IaC tool preference: Terraform vs Pulumi vs AWS CDK vs Ansible",
    "Cloud provider preference: AWS vs Azure vs GCP vs Multi-cloud",
    "Monitoring stack: Prometheus+Grafana vs Datadog vs New Relic vs CloudWatch",
    "Scripting language preference: Bash vs Python vs PowerShell vs Go",
    "GitOps tool: ArgoCD vs Flux vs Jenkins X vs Spinnaker",
    "Secret management: HashiCorp Vault vs AWS Secrets Manager vs Azure Key Vault",
    "Container registry: Docker Hub vs AWS ECR vs GitHub Packages vs self-hosted",
    "Logging stack: ELK vs Loki vs Splunk vs CloudWatch Logs",
    "Kubernetes ingress controller: Nginx vs Traefik vs HAProxy vs Istio",
    "Biggest DevOps bottleneck: Slow pipelines vs Flaky tests vs Manual approvals vs Bad docs",
    "DevOps certification priority: CKA vs AWS SAA vs Terraform Associate vs GCP Pro",
    "Infrastructure deployment frequency: Multiple per day vs Daily vs Weekly vs Monthly",
    "On-call tool preference: PagerDuty vs OpsGenie vs VictorOps vs Slack alerts",
    "Package manager preference: Helm vs Kustomize vs raw YAML vs Operator",
    "Most used kubectl command: get pods vs describe vs logs vs exec",
    "Biggest K8s pain point: YAML complexity vs Networking vs Security vs Cost",
    "Preferred Linux distro: Ubuntu vs CentOS vs Amazon Linux vs Alpine",
    "Service mesh preference: Istio vs Linkerd vs Consul Connect vs no mesh",
    "Database backup strategy: Automated scripts vs Managed snapshots vs Velero vs Custom",
    "Most impactful DevOps practice: CI/CD vs IaC vs Monitoring vs GitOps",
    "Deployment strategy preference: Blue-green vs Canary vs Rolling vs Recreate",
    "Remote work tool for DevOps teams: Slack vs Teams vs Discord vs Zoom",
    "Code review process: PR reviews vs Pair programming vs Automated only vs None",
    "Biggest cloud cost waste: Idle EC2 vs Over-provisioned RDS vs Unused ELBs vs Data transfer",
    "Preferred Terraform backend: S3+DynamoDB vs Terraform Cloud vs GitLab vs Local",
    "Incident response tool: Runbooks vs PagerDuty runbooks vs Confluence vs Notion",
    "Most useful DevOps metric: DORA metrics vs SLO/SLA vs MTTR vs Deploy frequency",
    "Docker base image preference: Alpine vs Debian slim vs Distroless vs Ubuntu",
    "Preferred pipeline trigger: Push to main vs PR merge vs Manual vs Tag push",
    "K8s resource management: Requests+limits vs VPA vs HPA vs KEDA",
    "Most used AWS service: EC2 vs Lambda vs EKS vs S3",
    "DevOps documentation tool: Confluence vs Notion vs GitHub Wiki vs GitBook",
    "Container runtime preference: Docker vs containerd vs CRI-O vs Podman",
    "Testing in CI/CD: Unit only vs Unit+Integration vs Full E2E vs Contract tests",
    "Kubernetes version upgrade strategy: Manual vs Managed vs Blue-green cluster vs Rolling",
    "DevOps team structure: Platform team vs Embedded vs SRE model vs Full DevOps ownership",
    "Favorite DevOps learning resource: YouTube vs Udemy vs KodeKloud vs Official docs",
    "Biggest security concern: Exposed secrets vs Unpatched CVEs vs Overprivileged IAM vs Supply chain",
]

# Slot 2 — Relatable Meme topics (40 unique funny DevOps situations)
SLOT2_TOPICS = [
    "terraform destroy accidentally deleting prod",
    "pipeline failing on Friday at 5pm",
    "kubectl debugging a CrashLoopBackOff at 3am",
    "YAML indentation error breaking the entire deployment",
    "'works on my machine' but fails in CI",
    "AWS bill shock from a forgotten EC2 instance",
    "Jenkins job running for 3 hours with no logs",
    "merge conflict in Terraform state file",
    "on-call pager going off during vacation",
    "docker build cache being invalidated for no reason",
    "Kubernetes pod stuck in Pending state with no explanation",
    "accidentally pushing secrets to GitHub",
    "Helm upgrade rolling back automatically at 2am",
    "explaining to management why the pipeline takes 45 minutes",
    "100 Dependabot PRs arriving on Monday morning",
    "staging environment being 'mostly like prod'",
    "reading someone else's undocumented bash script",
    "terraform plan showing 'destroy 47 resources'",
    "Kubernetes node running at 100% CPU with no obvious cause",
    "adding 'just one more environment variable' to fix prod",
    "the only person who knows how Jenkins works leaving the company",
    "docker container working locally but failing in K8s",
    "debugging a flaky test that only fails in CI not locally",
    "being on-call for a service with zero documentation",
    "CloudFormation rollback taking longer than the deployment",
    "GitLab runner running out of disk space mid-pipeline",
    "accidentally deleting the wrong S3 bucket",
    "Ansible playbook running for 2 hours on 'Gathering Facts'",
    "opening 15 browser tabs to debug one Kubernetes networking issue",
    "the monitoring alert that fires every day and nobody knows why",
    "deploying a hotfix and breaking 3 other services",
    "explaining why 99.9% uptime still means 8 hours of downtime per year",
    "git bisect finding the bug was introduced 2 years ago",
    "the VPN that disconnects exactly when you're in the middle of an SSH session",
    "reading the error logs and finding 'Error: Something went wrong'",
    "ArgoCD showing OutOfSync for 3 days with no one noticing",
    "the Prometheus alert that wakes you up but resolves by the time you check",
    "spending 4 hours debugging only to find a missing semicolon in a ConfigMap",
    "Kubernetes autoscaler scaling down the node your pod was on",
    "the load balancer health check failing because of a trailing slash",
]

# Slot 3 — Career Tip topics (40 unique DevOps career advice topics)
SLOT3_TOPICS = [
    "How to get your first DevOps job with no experience",
    "Top certifications every DevOps engineer needs in 2025",
    "How to build a DevOps portfolio on GitHub that gets you hired",
    "How to negotiate a higher salary as a DevOps engineer",
    "Skills to learn to go from Junior to Senior DevOps in 2 years",
    "How to contribute to open source as a DevOps engineer",
    "How to ace the CKA (Certified Kubernetes Administrator) exam",
    "Why every DevOps engineer should learn Python in 2025",
    "How to write a DevOps resume that passes ATS screening",
    "How to transition from SysAdmin to DevOps engineer",
    "Top 5 DevOps projects to put on your resume",
    "How to prepare for a DevOps technical interview",
    "Why learning Terraform will double your DevOps salary",
    "How to become a Site Reliability Engineer (SRE) in 2025",
    "How to get AWS Solutions Architect certification in 30 days",
    "Why every DevOps engineer should have a home lab",
    "How to learn Kubernetes for free in 2025",
    "DevOps roadmap for complete beginners in 2025",
    "How to get promoted from DevOps Engineer to Lead/Manager",
    "Why soft skills matter more than tools in DevOps",
    "How to build your personal brand as a DevOps engineer on LinkedIn",
    "Top 5 GitHub repos every DevOps engineer should study",
    "How to switch from developer to DevOps engineer",
    "Why every DevOps engineer should learn Go in 2025",
    "How to pass the Terraform Associate certification exam",
    "How to land a remote DevOps job at a US company from India",
    "Why reading postmortems makes you a better DevOps engineer",
    "How to set up a DevOps lab using free cloud credits",
    "Top DevOps YouTube channels to follow in 2025",
    "How to document your infrastructure like a senior DevOps engineer",
    "Why networking matters more than certifications in DevOps",
    "How to get into platform engineering from DevOps",
    "Top mistakes junior DevOps engineers make and how to avoid them",
    "How to build a CI/CD portfolio project from scratch",
    "Why every DevOps engineer should learn cloud cost optimization",
    "How to prepare for a DevOps system design interview",
    "Top freelance platforms for DevOps engineers to find work",
    "How to stay updated with DevOps trends without burning out",
    "Why contributing to CNCF projects boosts your DevOps career",
    "How to get a DevOps internship while still in college",
]

# Slot 4 — Motivational topics (40 unique motivational angles)
SLOT4_TOPICS = [
    "starting your DevOps journey from scratch with no CS degree",
    "pushing through the Kubernetes learning curve",
    "overcoming imposter syndrome as a DevOps engineer",
    "building your first CI/CD pipeline from zero",
    "learning Terraform when infrastructure feels overwhelming",
    "staying consistent when DevOps feels too hard",
    "getting your first DevOps job after months of rejection",
    "building in public even when nobody is watching",
    "studying for certifications while working full-time",
    "making mistakes in prod and coming back stronger",
    "learning cloud from scratch with no prior experience",
    "transitioning to DevOps after years in a different field",
    "contributing to open source for the first time",
    "setting up your home lab when resources are limited",
    "consistency beats intensity in learning DevOps tools",
    "the compound effect of learning one DevOps tool per month",
    "shipping your first automation script that saves hours",
    "how every senior DevOps engineer was once a beginner",
    "learning from production incidents instead of fearing them",
    "why the DevOps community is one of the best to be part of",
    "building your GitHub profile one commit at a time",
    "why failing the CKA exam the first time is not the end",
    "the moment your first pipeline deploys successfully",
    "how 30 minutes of learning DevOps daily compounds over a year",
    "why asking for help in the DevOps community is a strength",
    "embracing the chaos of DevOps and growing through it",
    "how reading postmortems makes you a better engineer",
    "why every automation you build saves future-you hours",
    "the power of documenting your learning journey publicly",
    "how one good DevOps project can change your career trajectory",
    "why every DevOps engineer should blog about what they learn",
    "how the best DevOps engineers are forever students",
    "why your background doesn't define your DevOps potential",
    "the satisfaction of a zero-downtime deployment you built",
    "how open source contributions open career doors",
    "why helping others learn DevOps accelerates your own growth",
    "the mindset shift from fixing problems to preventing them",
    "why mastering one cloud provider beats knowing three superficially",
    "how to keep learning when your day job exhausts you",
    "why building small daily habits beats weekend DevOps marathons",
]

# Slot 5 — Community Question topics (40 unique discussion starters)
SLOT5_TOPICS = [
    "the worst production incident you ever caused or witnessed",
    "the most useful DevOps tool nobody talks about",
    "the biggest lie in DevOps job descriptions",
    "what you wish you knew before starting your DevOps career",
    "the most important skill that made you a better DevOps engineer",
    "your honest opinion on Kubernetes complexity vs value",
    "the DevOps practice that changed how your team works",
    "the command you run every single day as a DevOps engineer",
    "your experience with on-call — is it worth the stress?",
    "the certification that actually helped your career vs ones that didn't",
    "your biggest Terraform mistake and what you learned",
    "what your current monitoring stack looks like and why",
    "the interview question that stumped you the most",
    "your opinion on Platform Engineering vs traditional DevOps",
    "the one tool you would remove from your stack if you could",
    "your experience switching from on-prem to cloud",
    "the most underrated DevOps practice in your opinion",
    "your take on DevOps engineers vs SRE — same or different?",
    "the project you are most proud of as a DevOps engineer",
    "your honest review of your current CI/CD tool",
    "what your ideal DevOps team structure looks like",
    "the technical debt you inherited that haunts you",
    "your experience with service meshes — worth the complexity?",
    "the book or resource that most influenced your DevOps thinking",
    "your take on GitOps — hype or the future?",
    "what your on-call rotation looks like and how you survive it",
    "the biggest cloud cost mistake your team ever made",
    "your experience with zero-downtime deployments — achievable or myth?",
    "the worst piece of DevOps advice you ever received",
    "your opinion on AI tools like Copilot in DevOps workflows",
    "the metric you track that nobody else on your team cares about",
    "your honest take on microservices vs monolith in 2025",
    "what you would automate first if you joined a new team",
    "the security gap you see most often in DevOps teams",
    "your experience with FinOps — do engineers care about cloud cost?",
    "the documentation practice that saved your team during an incident",
    "your take on serverless — future of DevOps or niche use case?",
    "what separates a good DevOps engineer from a great one",
    "the deployment strategy your team uses and why you chose it",
    "your advice to someone who just got their first DevOps job",
]

ALL_TOPICS = [
    SLOT0_TOPICS,  # Slot 0 — Project Post
    SLOT1_TOPICS,  # Slot 1 — Poll
    SLOT2_TOPICS,  # Slot 2 — Relatable Meme
    SLOT3_TOPICS,  # Slot 3 — Career Tip
    SLOT4_TOPICS,  # Slot 4 — Motivational
    SLOT5_TOPICS,  # Slot 5 — Community Question
]


def get_todays_topic(slot: int) -> str:
    """Pick topic based on day-of-year so each slot gets a DIFFERENT topic daily."""
    day   = datetime.utcnow().timetuple().tm_yday   # 1–365
    pool  = ALL_TOPICS[slot]
    # Each slot uses a different offset so slot 0 and slot 1 never pick the same index
    index = (day - 1 + slot * 7) % len(pool)
    return pool[index]


# ── Prompt templates per slot ─────────────────────────────────────────────────
def build_prompt(slot: int, topic: str, date: str) -> str:

    if slot == 0:
        return f"""You are a DevOps educator tweeting as @rajaji2.
Write ONE tweet about this exact topic: {topic}

STRICT FORMAT — copy this structure exactly:
{topic} like a DevOps Engineer!

✅ <specific feature/step 1>
✅ <specific feature/step 2>
✅ <specific feature/step 3>
✅ <specific feature/step 4>
✅ <specific feature/step 5>

#<tag1> #<tag2> #<tag3> #<tag4> #<tag5> #<tag6> #<tag7> #<tag8>

Rules:
- The 5 checkmarks must be specific to "{topic}" — not generic
- Pick 8 relevant hashtags for the topic
- Do NOT mention Helm Charts or Kubernetes unless the topic is about them
- Return ONLY the tweet text. No quotes. No explanation."""

    elif slot == 1:
        return f"""You are a DevOps community builder tweeting as @rajaji2.
Write ONE poll tweet about this topic: {topic}

STRICT FORMAT:
<Question about {topic}?>

🔵 <Option A>
🟢 <Option B>
🟡 <Option C>
🔴 <Option D>

#<tag1> #<tag2> #<tag3> #<tag4>

Return ONLY the tweet text. No quotes. No explanation."""

    elif slot == 2:
        return f"""You are a DevOps/SRE engineer venting on X as @rajaji2.
Write ONE funny relatable tweet about this situation: {topic}

Use this format:
Me: <action related to the situation>
<Tool or System>: <unexpected/annoying response>
Me: <frustrated or funny reaction>

OR this format:
<Relatable one-liner about the situation>
<punchline or continuation>

Keep it short, punchy, and funny. End with 1-2 relevant hashtags.
Return ONLY the tweet text. No quotes. No explanation."""

    elif slot == 3:
        return f"""You are a senior DevOps engineer mentoring others as @rajaji2.
Write ONE career tip tweet about: {topic}

STRICT FORMAT:
<Bold tip title related to {topic}> 🎯

✔️ <specific actionable tip 1>
✔️ <specific actionable tip 2>
✔️ <specific actionable tip 3>
✔️ <specific actionable tip 4>

#<tag1> #<tag2> #<tag3> #<tag4> #<tag5>

Return ONLY the tweet text. No quotes. No explanation."""

    elif slot == 4:
        return f"""You are a DevOps engineer motivating others as @rajaji2.
Write ONE motivational tweet about: {topic}

STRICT FORMAT:
<Powerful opening statement about {topic}>

💪 <specific encouragement point 1>
💪 <specific encouragement point 2>
💪 <specific encouragement point 3>

🔥 <strong closing line>

#<tag1> #<tag2> #<tag3> #<tag4>

Return ONLY the tweet text. No quotes. No explanation."""

    elif slot == 5:
        return f"""You are a DevOps community builder tweeting as @rajaji2.
Write ONE question tweet to spark discussion about: {topic}

STRICT FORMAT:
<Engaging question about {topic}?> 🤔

Drop your answer below 👇

#<tag1> #<tag2> #<tag3> #<tag4>

The question must be genuinely interesting and specific to the topic.
Return ONLY the tweet text. No quotes. No explanation."""

    return f"Write a DevOps tweet about {topic}. Under 280 chars."


# ── Claude API call ───────────────────────────────────────────────────────────
def generate_tweet(slot: int) -> str:
    topic    = get_todays_topic(slot)
    date_str = datetime.utcnow().strftime("%A %B %d %Y")
    prompt   = build_prompt(slot, topic, date_str)

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


# ── Post to X ─────────────────────────────────────────────────────────────────
def post_tweet(text: str) -> str:
    client = tweepy.Client(
        consumer_key        = X_API_KEY,
        consumer_secret     = X_API_SECRET,
        access_token        = X_ACCESS_TOKEN,
        access_token_secret = X_ACCESS_SECRET,
    )
    resp = client.create_tweet(text=text)
    return resp.data["id"]


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    labels = ["Project Post", "Poll", "Relatable Meme", "Career Tip", "Motivational", "Community Question"]
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
