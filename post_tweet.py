#!/usr/bin/env python3
"""
X (Twitter) Auto-poster for @rajaji2
DevOps / CI-CD / Cloud niche
No external AI API needed — uses a built-in tweet bank (200+ tweets)
Rotates daily so content never repeats for months
"""

import os
import tweepy
import hashlib
from datetime import datetime, date

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
X_API_KEY       = os.environ["X_API_KEY"]
X_API_SECRET    = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN  = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]

# ── Tweet slot (0–4) passed by GitHub Actions ─────────────────────────────────
SLOT = int(os.environ.get("TWEET_SLOT", "0"))

# ═════════════════════════════════════════════════════════════════════════════
# TWEET BANK — 5 categories × 40 tweets each = 200 tweets
# Content rotates daily using a date-based index — no repeats for 40 days
# ═════════════════════════════════════════════════════════════════════════════

SLOT_0_PROJECT = [
    "🚀 Today's project: Build a GitHub Actions CI pipeline that lints, tests & pushes a Docker image on every commit. 3-min setup, real-world skills. Try it! #GitHubActions #CICD #DevOps",
    "⚙️ Today's project: Provision an AWS EC2 + S3 bucket with Terraform in under 50 lines of HCL. Infra as code from scratch! #Terraform #AWS #IaC",
    "🐳 Today's project: Shrink your Docker image from 800MB → 50MB using multi-stage builds. One Dockerfile change, massive impact. #Docker #DevOps #Containers",
    "☸️ Today's project: Configure a K8s rolling update with readiness probes — zero downtime deploys on every push. #Kubernetes #Helm #CloudNative",
    "📊 Today's project: Spin up Prometheus + Grafana with Docker Compose and alert when CPU > 80%. Full monitoring in 10 min! #Monitoring #Grafana #Observability",
    "🔄 Today's project: Set up ArgoCD to auto-sync your K8s cluster from a Git repo. Every git push = live deployment. #GitOps #ArgoCD #CICD",
    "🌐 Today's project: Route traffic to 3 services with one Nginx container + add SSL via Let's Encrypt. #Nginx #Docker #DevOps",
    "🔐 Today's project: Add Trivy image scanning to your CI pipeline — catch vulnerabilities before they hit prod. #DevSecOps #CICD #Docker",
    "📦 Today's project: Build a Helm chart from scratch and deploy it to a local Kind cluster. #Kubernetes #Helm #CloudNative",
    "⚡ Today's project: Speed up your GitHub Actions workflow 3x using layer caching + dependency caching. #GitHubActions #CICD #DevOps",
    "🏗️ Today's project: Create reusable Terraform modules for VPC + EC2 + RDS. DRY infra that scales. #Terraform #IaC #AWS",
    "🕵️ Today's project: Set up Loki + Grafana for centralized log aggregation across all your Docker containers. #Observability #Grafana #DevOps",
    "🚦 Today's project: Write a K8s NetworkPolicy to isolate your frontend from your DB — zero-trust networking. #Kubernetes #Security #CloudNative",
    "🤖 Today's project: Build a self-hosted GitHub Actions runner on a free Oracle Cloud VM. #GitHubActions #DevOps #Cloud",
    "📋 Today's project: Create a GitLab CI pipeline with stages: build → test → scan → deploy. Full DevSecOps flow! #GitLabCI #CICD #DevSecOps",
    "🔑 Today's project: Manage Kubernetes secrets properly using Sealed Secrets — encrypt at rest in Git. #Kubernetes #Security #GitOps",
    "🌍 Today's project: Deploy a multi-region setup on AWS using Terraform with automatic failover. #Terraform #AWS #IaC",
    "📈 Today's project: Set up HPA (Horizontal Pod Autoscaler) in K8s — auto-scale on CPU/memory load. #Kubernetes #CloudNative #DevOps",
    "🛡️ Today's project: Add OWASP ZAP security scanning to your CI/CD pipeline in 15 minutes. #DevSecOps #CICD #Security",
    "🐙 Today's project: Build a GitHub Actions matrix to test your app on Python 3.10, 3.11 & 3.12 simultaneously. #GitHubActions #CICD #Python",
    "💾 Today's project: Automate PostgreSQL backups to S3 with a simple bash script + cron job. #DevOps #AWS #Backup",
    "🔧 Today's project: Build a custom Grafana dashboard for your K8s cluster — CPU, memory, pod health at a glance. #Grafana #Kubernetes #Observability",
    "🚢 Today's project: Deploy your first app to AWS EKS using eksctl + kubectl in under 30 minutes. #AWS #Kubernetes #DevOps",
    "⚓ Today's project: Set up Docker Swarm for multi-host container orchestration without the K8s complexity. #Docker #DevOps #Containers",
    "🔁 Today's project: Create a blue-green deployment pipeline with GitHub Actions + AWS ECS. Zero-downtime releases! #CICD #AWS #DevOps",
    "🧪 Today's project: Add integration tests to your CI pipeline using Docker Compose service containers. #CICD #Docker #Testing",
    "🌲 Today's project: Set up Fluentd to ship logs from K8s pods to Elasticsearch. Full EFK stack! #Kubernetes #Observability #DevOps",
    "⚡ Today's project: Build a serverless CI/CD pipeline using AWS Lambda + CodePipeline. #AWS #Serverless #CICD",
    "🏠 Today's project: Self-host your own container registry with Harbor on a $5 VPS. #Docker #DevOps #Security",
    "🔍 Today's project: Set up Jaeger distributed tracing in a microservices app — find bottlenecks instantly. #Observability #Microservices #DevOps",
    "🛠️ Today's project: Write an Ansible playbook to configure 10 servers identically in 2 minutes. #Ansible #IaC #DevOps",
    "📡 Today's project: Build a Kubernetes Operator from scratch using the Operator SDK. #Kubernetes #CloudNative #DevOps",
    "🔒 Today's project: Implement Pod Security Admission in K8s — enforce security standards cluster-wide. #Kubernetes #Security #DevOps",
    "🌊 Today's project: Set up Istio service mesh for traffic management + mTLS in Kubernetes. #Kubernetes #ServiceMesh #CloudNative",
    "📦 Today's project: Build a private npm/PyPI package registry with Verdaccio + Docker. #DevOps #Containers #DevEx",
    "🚀 Today's project: Deploy a static site to AWS S3 + CloudFront via GitHub Actions — full CI/CD in 20 min. #AWS #CICD #DevOps",
    "🔐 Today's project: Rotate AWS IAM credentials automatically with a Lambda function. #AWS #Security #Automation",
    "📊 Today's project: Build a custom Prometheus exporter in Python for your app's business metrics. #Prometheus #Observability #DevOps",
    "🤖 Today's project: Automate K8s cluster upgrades with a GitHub Actions workflow + health checks. #Kubernetes #CICD #DevOps",
    "🧹 Today's project: Set up automated Docker image cleanup with a daily cron job — reclaim disk space. #Docker #DevOps #Automation",
]

SLOT_1_TIP = [
    "💡 Use `docker system prune -af --volumes` to reclaim disk space. Removes all unused containers, images, networks & volumes. Schedule it weekly in cron. #Docker #DevOps",
    "💡 Add `--cache-from` in your Dockerfile builds on CI to reuse layer cache across runs:\n`docker build --cache-from myapp:latest .`\nCuts build time by 60-80%. #Docker #CICD",
    "💡 Always set resource limits in K8s. Without them, one pod can starve the entire node:\n```\nresources:\n  limits:\n    memory: '256Mi'\n    cpu: '500m'\n``` #Kubernetes #DevOps",
    "💡 Use `kubectl rollout undo deployment/myapp` to instantly revert a bad deployment. Saved by rollout history! Always keep `revisionHistoryLimit: 3`. #Kubernetes #DevOps",
    "💡 Terraform tip: Always run `terraform plan -out=tfplan` and apply the saved plan:\n`terraform apply tfplan`\nNo surprises from env changes between plan & apply. #Terraform #IaC",
    "💡 GitHub Actions: Cache your pip/npm dependencies to save 2-3 min per run:\n```\n- uses: actions/cache@v3\n  with:\n    path: ~/.cache/pip\n    key: ${{ hashFiles('requirements.txt') }}\n``` #GitHubActions #CICD",
    "💡 Use `kubectl top pods --sort-by=memory` to instantly find your memory-hungry pods. Great first step before setting resource limits. #Kubernetes #DevOps",
    "💡 Terraform: Use `terraform state mv` to rename resources without destroying them. Beats delete + recreate every time. #Terraform #IaC #DevOps",
    "💡 Set `DOCKER_BUILDKIT=1` before every docker build. BuildKit parallelizes stages and skips unused ones. Free speed boost. #Docker #DevOps",
    "💡 Use AWS SSM Parameter Store instead of hardcoding secrets in env vars. Free, encrypted, auditable. `aws ssm get-parameter --name /app/secret --with-decryption` #AWS #Security",
    "💡 Add `--fail-fast` to your test stage so your CI pipeline stops immediately on first failure. No waiting for 20 more tests to finish. #CICD #DevOps",
    "💡 K8s liveness vs readiness probes:\n- Liveness: restart pod if unhealthy\n- Readiness: remove from load balancer if not ready\nUse both. They solve different problems. #Kubernetes",
    "💡 `git bisect` finds the exact commit that broke your pipeline. Run `git bisect start`, mark good/bad commits. Git does a binary search. Saves hours. #Git #DevOps",
    "💡 Use multi-stage Docker builds to keep your final image tiny:\nStage 1 (builder): compile/install deps\nStage 2 (runtime): copy only the binary\nResult: 90% smaller images. #Docker",
    "💡 Terraform: Never store `.tfstate` locally. Use S3 + DynamoDB backend for locking:\n```\nbackend \"s3\" {\n  bucket = \"my-tfstate\"\n  key    = \"prod/terraform.tfstate\"\n  dynamodb_table = \"tf-lock\"\n}\n``` #Terraform #AWS",
    "💡 Use `kubectl describe pod <name>` before `kubectl logs`. Describe shows scheduling errors, image pull failures & OOMKilled events that logs misses. #Kubernetes",
    "💡 GitHub Actions matrix strategy lets you test across multiple OS/versions in parallel:\n```\nstrategy:\n  matrix:\n    python-version: [3.10, 3.11, 3.12]\n``` #GitHubActions #CICD",
    "💡 Add `set -euo pipefail` to every bash script in your CI pipeline. Fails fast on any error, undefined variable, or broken pipe. Essential for safe automation. #DevOps #Bash",
    "💡 Use `docker-compose --profile prod up` to start only prod services. Define profiles per service to avoid running dev tools in staging. #Docker #DevOps",
    "💡 ArgoCD tip: Use `syncPolicy.automated.selfHeal: true` to auto-fix manual cluster changes. Your Git repo always wins. True GitOps. #ArgoCD #GitOps #Kubernetes",
    "💡 AWS cost tip: Use `aws ce get-cost-and-usage` in your CI pipeline to alert on spend anomalies before your monthly bill surprises you. #AWS #FinOps #DevOps",
    "💡 K8s: Use `PodDisruptionBudget` to guarantee availability during node drains:\n`minAvailable: 2` ensures at least 2 pods always run. Essential for prod. #Kubernetes #DevOps",
    "💡 Helm tip: Use `helm diff upgrade` (helm-diff plugin) to preview exactly what will change before applying. Like `terraform plan` for K8s. #Helm #Kubernetes",
    "💡 Use `kubectl exec -it <pod> -- sh` to debug inside a running container. Faster than rebuilding images. Combine with `netstat` and `curl` for network debugging. #Kubernetes",
    "💡 Prometheus: Use `rate()` not `irate()` for dashboards. `rate()` is more resilient to scrappe gaps and gives smoother graphs. Use `irate()` only for spikes. #Prometheus #Observability",
    "💡 Add `dependabot.yml` to auto-update your GitHub Actions versions:\n```\npackage-ecosystem: 'github-actions'\ndirectory: '/'\nschedule:\n  interval: 'weekly'\n``` #GitHubActions #Security",
    "💡 Use `terraform output -json` to pipe infra values into your deployment scripts. No hardcoding IPs or ARNs in CI/CD. #Terraform #IaC #CICD",
    "💡 K8s: Label everything consistently — `app`, `env`, `version`, `team`. Then filter with:\n`kubectl get pods -l env=prod,team=backend`\nSaves hours of debugging. #Kubernetes #DevOps",
    "💡 Use `docker buildx` for multi-platform builds (amd64 + arm64) from one command:\n`docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .` #Docker #DevOps",
    "💡 Grafana tip: Use template variables in dashboards so one dashboard works for all environments. `$namespace`, `$cluster` dropdowns = one dashboard to rule them all. #Grafana #Observability",
    "💡 Always pin your Action versions with SHA, not tags:\n`uses: actions/checkout@abc123` not `@v4`\nTags can be overwritten. SHA commits are immutable. #GitHubActions #Security",
    "💡 Use `kubectl get events --sort-by='.lastTimestamp'` to see recent cluster events in order. First place to look when a pod won't start. #Kubernetes #DevOps",
    "💡 Terraform: Use `moved {}` blocks to rename resources without destroying them — no more scary `destroy + create` plans for simple refactors. #Terraform #IaC",
    "💡 Add health check endpoints (`/healthz`, `/readyz`) to every service. K8s, load balancers, and monitoring all depend on them. Make them free of auth. #DevOps #Kubernetes",
    "💡 Use `COPY --chown=node:node` in Dockerfiles to avoid running as root. One line, big security win. #Docker #DevSecOps #Security",
    "💡 GitHub Actions: Use `workflow_dispatch` inputs to run manual deployments with parameters directly from the GitHub UI. No more SSH deployments. #GitHubActions #CICD",
    "💡 Use `kubectl rollout status deployment/myapp --timeout=120s` in CI to block until deploy succeeds. Fail the pipeline if rollout doesn't complete. #Kubernetes #CICD",
    "💡 Terraform: `terraform import` lets you bring existing cloud resources under IaC control without recreating them. Start managing legacy infra today. #Terraform #IaC",
    "💡 Use `docker stats` to see real-time CPU/memory per container. Much faster than installing monitoring for a quick debug session. #Docker #DevOps",
    "💡 Add `concurrency` to GitHub Actions to cancel in-progress runs when a new commit is pushed. Saves CI minutes and avoids race conditions:\n`concurrency:\n  group: ${{ github.ref }}\n  cancel-in-progress: true` #GitHubActions",
]

SLOT_2_HOTTAKE = [
    "Hot take: If your deployment takes more than 10 minutes, you don't have a CI/CD pipeline — you have a slow manual process with extra steps. #DevOps #CICD",
    "Unpopular opinion: Most teams don't need Kubernetes. A single well-configured VM with Docker Compose would serve them better and cost 80% less. #Kubernetes #DevOps",
    "Hot take: 'Infrastructure as Code' done with ClickOps notes in a Notion doc is not IaC. It's documentation of technical debt. #Terraform #IaC #DevOps",
    "Unpopular opinion: The real DevOps bottleneck isn't tools — it's the team that gates every deploy behind a 3-day change approval process. #DevOps #Culture",
    "Hot take: If your on-call runbook says 'restart the pod', you don't have a runbook — you have a panic button with instructions. Fix the root cause. #SRE #DevOps",
    "Unpopular opinion: GitOps sounds great until your Git repo and cluster are out of sync and nobody knows which is the source of truth anymore. #GitOps #DevOps",
    "Hot take: YAML is not a programming language. Stop putting business logic in your K8s manifests. That's what Helm and Kustomize are for. #Kubernetes #DevOps",
    "Unpopular opinion: Monitoring dashboards nobody watches aren't monitoring — they're expensive screen savers. Alerts that page the right person matter more. #Observability #SRE",
    "Hot take: If your developers can't deploy on their own, you don't have DevOps — you have Dev and Ops with a shared Slack channel. #DevOps #Culture",
    "Unpopular opinion: Microservices are the right answer for maybe 10% of teams. The other 90% created a distributed monolith and called it modern architecture. #DevOps #Microservices",
    "Hot take: The best DevOps tool isn't Terraform, K8s, or ArgoCD — it's a blameless postmortem culture. Tools don't fix broken processes. #DevOps #SRE",
    "Unpopular opinion: Helm charts are YAML that hates you, wrapped in Go templates that hate readability. But we use them anyway because the alternative is worse. #Kubernetes #Helm",
    "Hot take: A 99.9% uptime SLA means 8.7 hours of downtime per year is acceptable. Most teams celebrate this. SREs lose sleep over it. #SRE #DevOps",
    "Unpopular opinion: Most 'DevSecOps' is just adding a vulnerability scanner to CI that everyone ignores because it flags 400 issues on day one. #DevSecOps #Security",
    "Hot take: The cloud isn't cheaper — it's more convenient. If your AWS bill shocked you, you bought convenience and called it cost savings. #AWS #FinOps #Cloud",
    "Unpopular opinion: Feature flags are more powerful than blue-green deployments. You can turn off a bad feature in 10 seconds without a rollback. #DevOps #CICD",
    "Hot take: If your staging environment doesn't match prod, it's not a staging environment — it's a false sense of security. #DevOps #Testing",
    "Unpopular opinion: Container security is mostly theater. Most teams scan images but run containers as root with no NetworkPolicy. Fix the basics first. #DevSecOps #Docker",
    "Hot take: Terraform state corruption is not a bug — it's a warning that you're letting multiple people run apply without remote state locking. Fix the process. #Terraform #IaC",
    "Unpopular opinion: On-call rotations without blameless postmortems just create burnout and hero engineers. Sustainability requires systemic fixes, not heroes. #SRE #DevOps",
    "Hot take: Your pipeline isn't automated if someone still has to approve every prod deploy at 2am because 'someone needs to watch it'. That's just slow manual work. #CICD #DevOps",
    "Unpopular opinion: Service meshes like Istio add more complexity than most teams can manage. mTLS + circuit breakers sound great until your mesh goes down. #Kubernetes #ServiceMesh",
    "Hot take: The #1 security vulnerability in most cloud environments isn't a CVE — it's an IAM role with `*:*` permissions someone added '2 years ago to fix something'. #AWS #Security",
    "Unpopular opinion: Docker Desktop is fine. You don't need to replace it with Colima/Podman/Rancher just to prove a point. Use what makes your team productive. #Docker #DevEx",
    "Hot take: If your incident postmortem ends with 'human error' as the root cause, you haven't done a postmortem — you've done blame assignment. #SRE #DevOps",
    "Unpopular opinion: Most teams adopting platform engineering are just rebranding their DevOps team and buying new tools. Culture change is the hard part. #DevOps #PlatformEngineering",
    "Hot take: CI pipelines that take 45 minutes to run aren't protecting code quality — they're teaching developers to push large batches and avoid feedback. #CICD #DevOps",
    "Unpopular opinion: FinOps isn't about cutting cloud costs — it's about aligning cloud spend with business value. Big difference. Cost cutting kills innovation. #FinOps #AWS #Cloud",
    "Hot take: The most underrated DevOps skill isn't Kubernetes or Terraform — it's being able to write a clear incident report that prevents the next one. #SRE #DevOps",
    "Unpopular opinion: Serverless is excellent for specific use cases and terrible when used as a default architecture. Not everything should be a Lambda function. #AWS #Serverless #DevOps",
    "Hot take: Your MTTR matters more than your MTBF. In complex systems, failures are inevitable. The differentiator is how fast you recover. #SRE #Observability",
    "Unpopular opinion: Most K8s clusters are massively over-provisioned because nobody trusts HPA. Set proper resource requests and let autoscaling do its job. #Kubernetes #FinOps",
    "Hot take: If your 'DevOps engineer' is just a sysadmin who learned Docker, that's fine — but don't expect them to transform your engineering culture alone. #DevOps #Culture",
    "Unpopular opinion: The best pipeline is the one your developers actually understand and can debug themselves. Black-box automation creates fragile systems. #CICD #DevOps",
    "Hot take: Log aggregation without structured logging is just a searchable pile of noise. Add `level`, `trace_id`, and `service` to every log line. #Observability #DevOps",
    "Unpopular opinion: Most 'platform teams' solve the wrong problem. Developers don't want abstractions — they want fast feedback and self-service deployments. #PlatformEngineering #DevEx",
    "Hot take: The reason your infra keeps breaking isn't the tools — it's that nobody owns the runbooks. Undocumented systems fail silently until they fail loudly. #SRE #DevOps",
    "Unpopular opinion: Scheduled maintenance windows in 2026 are a choice, not a requirement. Blue-green deploys and feature flags exist specifically to eliminate them. #DevOps #CICD",
    "Hot take: 'We can't automate that deploy — it's too risky' usually means 'we haven't invested in the testing and rollback tooling to make automation safe'. #DevOps #CICD",
    "Unpopular opinion: Your CI/CD pipeline IS your product. Treat it with the same engineering discipline as your customer-facing code. Test it. Version it. Own it. #CICD #DevOps",
]

SLOT_3_POLL = [
    "What's your primary container orchestration platform in prod?\n\n☸️ Kubernetes (self-managed)\n🟠 EKS / GKE / AKS (managed)\n🐳 Docker Swarm\n🤷 Still evaluating\n\n#DevOps #Kubernetes #CloudNative",
    "What's your go-to IaC tool?\n\n🟣 Terraform\n🔵 Pulumi\n🟡 AWS CDK / CloudFormation\n🔧 Ansible\n\n#IaC #DevOps #Cloud",
    "How often does your team do production deployments?\n\n⚡ Multiple times a day\n📅 Once a day\n📆 Once a week\n😬 Once a month or less\n\n#CICD #DevOps",
    "Biggest pain point in your CI/CD pipeline right now?\n\n⏱️ Too slow (15+ min builds)\n🔥 Flaky tests\n🔐 Secrets management\n📦 Dependency hell\n\n#CICD #DevOps",
    "What's your team's on-call situation?\n\n😴 Rarely get paged\n😐 Manageable alerts\n😰 Alert fatigue is real\n💀 On-call is burning us out\n\n#SRE #DevOps #Observability",
    "Which Kubernetes distribution do you run?\n\n☸️ Vanilla K8s\n🚀 K3s / K3d\n🏠 Kind (local)\n☁️ Managed (EKS/GKE/AKS)\n\n#Kubernetes #DevOps #CloudNative",
    "How do you manage secrets in K8s?\n\n🔒 HashiCorp Vault\n🔑 Sealed Secrets\n☁️ AWS/GCP/Azure Secrets Manager\n😬 K8s Secrets (base64 😅)\n\n#Kubernetes #Security #DevOps",
    "What's your monitoring stack?\n\n📊 Prometheus + Grafana\n📈 Datadog\n🔍 ELK / EFK Stack\n☁️ Cloud-native (CloudWatch etc.)\n\n#Observability #DevOps #Monitoring",
    "How long does your full CI pipeline take?\n\n⚡ Under 5 minutes\n✅ 5-10 minutes\n⏳ 10-20 minutes\n😢 Over 20 minutes\n\n#CICD #GitHubActions #DevOps",
    "Which GitOps tool are you using?\n\n🐙 ArgoCD\n🌊 Flux\n🏗️ Jenkins X\n🤔 Not doing GitOps yet\n\n#GitOps #Kubernetes #DevOps",
    "What's your primary cloud provider?\n\n🟠 AWS\n🔵 Azure\n🟡 GCP\n🌐 Multi-cloud\n\n#Cloud #DevOps #AWS",
    "How do you handle database migrations in CI/CD?\n\n🔄 Flyway / Liquibase\n✍️ Manual SQL scripts\n🏗️ ORM migrations (Django/Rails)\n😅 Very carefully\n\n#DevOps #Database #CICD",
    "What's your container base image strategy?\n\n🪶 Distroless / Scratch\n🏔️ Alpine\n🐧 Debian Slim\n📦 Whatever works\n\n#Docker #DevSecOps #Containers",
    "Do you practice chaos engineering?\n\n🎯 Yes, regularly (Chaos Monkey etc.)\n🧪 Occasional game days\n📋 Planning to start\n😅 We have enough unplanned chaos\n\n#SRE #DevOps #ChaosEngineering",
    "How are you handling K8s cluster upgrades?\n\n🤖 Fully automated\n🔵 Managed service handles it\n📋 Manual with runbook\n😰 We're several versions behind\n\n#Kubernetes #DevOps",
    "What percentage of your infra is IaC?\n\n✅ 100% — fully codified\n📈 70-99% — almost there\n📊 30-70% — work in progress\n😬 Under 30% — lots of ClickOps\n\n#IaC #Terraform #DevOps",
    "Which CI/CD platform does your team use?\n\n🐙 GitHub Actions\n🦊 GitLab CI\n🔵 Jenkins\n🔄 CircleCI / Travis\n\n#CICD #DevOps",
    "How do you enforce code quality in CI?\n\n🔍 Linting + SAST scanning\n✅ Unit + integration tests only\n📋 Code review only\n🙈 It's on the TODO list\n\n#CICD #DevOps #DevSecOps",
    "What's your disaster recovery RTO target?\n\n⚡ Under 1 hour\n🕐 1-4 hours\n📅 Same business day\n🤷 We haven't defined one yet\n\n#SRE #DisasterRecovery #DevOps",
    "Do you have runbooks for your top 5 alerts?\n\n✅ Yes, kept up to date\n📋 Yes, but they're outdated\n🚧 Partially documented\n🆘 We figure it out when it happens\n\n#SRE #DevOps #Observability",
    "How do you handle feature releases?\n\n🏳️ Feature flags\n🔵🟢 Blue-green deployment\n🐤 Canary releases\n🤞 Ship and pray\n\n#DevOps #CICD #CloudNative",
    "What's your K8s resource request/limit strategy?\n\n📊 Tuned for every service\n🔄 Same limits for everything\n🎯 Starting to configure them\n😬 No limits set (living dangerously)\n\n#Kubernetes #DevOps",
    "How do you handle incident postmortems?\n\n📝 Blameless + action items tracked\n📋 We write them, rarely follow up\n🗣️ Verbal discussion only\n⏩ Skip — we fix and move on\n\n#SRE #DevOps",
    "What's your team's deployment pipeline?\n\n🤖 Fully automated to prod\n👆 Auto to staging, manual to prod\n📋 Manual with scripts\n🚀 Git push = FTP upload 😅\n\n#CICD #DevOps",
    "How often do your Prometheus alerts fire false positives?\n\n✅ Rarely — well-tuned\n📊 Sometimes — working on it\n🔔 Often — alert fatigue is real\n🤷 We don't have alerting yet\n\n#Prometheus #SRE #Observability",
    "What's your team size vs infra complexity?\n\n👤 Solo DevOps managing 50+ services\n👥 Small team, manageable infra\n🏢 Large team, complex infra\n😰 Small team, too complex infra\n\n#DevOps #SRE",
    "Which secret rotation strategy do you use?\n\n🔄 Fully automated rotation\n📅 Manual, scheduled rotation\n🔐 Rotated after incidents only\n😬 Set it and forget it\n\n#Security #DevOps #SecretManagement",
    "How do you validate your Terraform before apply?\n\n✅ Plan + automated policy (OPA/Sentinel)\n👀 Plan + manual review\n🏃 Apply directly (living on the edge)\n🧪 Only in dev environment\n\n#Terraform #IaC #DevOps",
    "What's your biggest Kubernetes challenge?\n\n📦 Resource management\n🔐 RBAC and security\n🌐 Networking complexity\n💰 Cost optimization\n\n#Kubernetes #DevOps #CloudNative",
    "How do you handle secrets in GitHub Actions?\n\n🔐 GitHub Secrets only\n🏗️ Vault / external secrets manager\n📄 .env files (please no)\n☁️ Cloud provider secrets (AWS SSM etc.)\n\n#GitHubActions #Security #DevOps",
    "What's your preferred local K8s setup?\n\n🏠 Kind\n🏃 Minikube\n🪶 K3d\n🐳 Docker Desktop K8s\n\n#Kubernetes #DevEx #DevOps",
    "How do you handle config differences across environments?\n\n🎯 Helm values per env\n🔀 Kustomize overlays\n📄 Separate YAML files\n🌿 Environment variables\n\n#Kubernetes #DevOps #GitOps",
    "What keeps you up at night as a DevOps/SRE engineer?\n\n🚨 Production incidents\n🔐 Security vulnerabilities\n💰 Unexpected cloud costs\n📦 Tech debt accumulation\n\n#SRE #DevOps",
    "How do you learn new DevOps tools?\n\n📖 Docs + hands-on labs\n🎓 Paid courses (KodeKloud, A Cloud Guru)\n🐙 Open source contributions\n🔥 Breaking prod and fixing it\n\n#DevOps #Learning",
    "What's your test coverage strategy for infra code?\n\n🧪 Terratest / kitchen-terraform\n✅ Checkov / tfsec static analysis\n👀 Manual review only\n😬 Tests? For infra?\n\n#Terraform #IaC #DevOps",
    "Which container runtime do you use in prod K8s?\n\n🐳 containerd\n🔴 CRI-O\n🐋 Docker (via dockershim, old school)\n🤷 Whatever the managed service uses\n\n#Kubernetes #Containers",
    "How do you handle K8s RBAC?\n\n📋 Least privilege, all documented\n🔧 Configured but could be tighter\n😅 Admin for everyone (we trust the team)\n🆘 No RBAC configured\n\n#Kubernetes #Security #DevOps",
    "What's your image vulnerability scanning setup?\n\n🔍 Trivy in CI pipeline\n🐡 Snyk integration\n☁️ Cloud registry scanning (ECR/GCR)\n😬 Manual, occasional scans\n\n#DevSecOps #Docker #Security",
    "How do you handle multi-cloud?\n\n☁️ We're all-in on one cloud\n🌐 Actively multi-cloud\n🔄 Cloud-agnostic with abstractions\n🤔 Planning to go multi-cloud\n\n#Cloud #DevOps #Terraform",
    "What's your SLO for your main service?\n\n✅ Defined, measured, met consistently\n📊 Defined but not always met\n🚧 Work in progress\n🤷 No formal SLOs yet\n\n#SRE #DevOps #Observability",
]

SLOT_4_MEME = [
    "It's Friday 5pm. Prod is red. The pipeline failed. Nobody knows why. The PR that broke it was merged 6 days ago. Classic. #DevOps #SRE",
    "Me: I'll just do a quick `terraform apply` to fix this one thing.\n\nTerraform: Plan: 47 to destroy, 63 to add, 12 to change.\n\nMe: ...let's review this carefully. #Terraform #DevOps",
    "The 5 stages of a Kubernetes outage:\n1. It's probably nothing\n2. kubectl describe everything\n3. Google the error\n4. It was a missing semicolon in a ConfigMap\n5. Write the postmortem #Kubernetes #SRE",
    "DevOps job posting: 'We need someone who knows Kubernetes, Terraform, AWS, GCP, Azure, Prometheus, Grafana, ArgoCD, Istio, and Vault.'\n\nSalary: Competitive 😅 #DevOps #Jobs",
    "Team: Why is prod down?\nMe: Working on it.\nTeam: What happened?\nMe: Working on it.\nTeam: When will it be fixed?\nMe: *mutes Slack* #SRE #OnCall #DevOps",
    "`works on my machine` is just an undocumented feature of your CI/CD pipeline. #Docker #DevOps #CICD",
    "Me: I'll containerize this app real quick.\n*4 hours later*\nMe: Why does it work with --privileged but not without? *opens 12 Stack Overflow tabs* #Docker #DevOps",
    "New DevOps engineer: I'll clean up these unused resources.\n*3 hours later*\nEveryone: Why is prod down? #AWS #DevOps #CloudCost",
    "The Kubernetes learning curve:\nDay 1: 'Wow this is powerful!'\nDay 7: 'I think I get it'\nDay 30: 'Why is this pod CrashLoopBackOff'\nDay 365: 'Why is this pod CrashLoopBackOff' #Kubernetes",
    "On-call rotation:\n- Mon: minor alert, fixed in 5 min ✅\n- Tue: nothing ✅\n- Wed: nothing ✅\n- Thu: nothing ✅\n- Fri 4:57pm: EVERYTHING IS ON FIRE 🔥 #SRE #OnCall #DevOps",
    "You: We need better observability.\nManagement: Add more dashboards.\nYou: That's... not what I meant.\nManagement: *points to 47 Grafana dashboards nobody reads* #Observability #DevOps",
    "My CI pipeline:\n- Lint: ✅ 30s\n- Unit tests: ✅ 2m\n- Build Docker image: ✅ 4m\n- Integration tests: ✅ 8m\n- Deploy to staging: ✅ 3m\n- 'Quick deploy' to prod: 18 minutes 😅 #CICD",
    "Interviewer: Describe your experience with failure.\nSRE: *laughs in on-call* #SRE #DevOps #Interview",
    "Git history of every infrastructure repo:\n- 'initial commit'\n- 'fix'\n- 'fix2'\n- 'actually fix'\n- 'hotfix'\n- 'hotfix_FINAL'\n- 'hotfix_FINAL_v2_USE_THIS_ONE' #DevOps #Git",
    "The two types of DevOps engineers:\n1. 'We need to automate everything!'\n2. *scripts break prod at 3am*\n1. 'We need to automate everything better!' #DevOps #Automation",
    "Terraform: Do you really want to destroy 1 resource?\n\nMe: Yes.\n\nTerraform: Are you sure?\n\nMe: Yes.\n\nTerraform: No going back.\n\nMe: *sweating* ...yes. #Terraform #DevOps #IaC",
    "Kubernetes YAML:\nLine 1: apiVersion\nLine 2: kind\nLine 3-400: indentation crimes\nLine 401: one wrong space = everything breaks #Kubernetes #DevOps",
    "DevOps in theory: Dev and Ops work together harmoniously.\nDevOps in practice: 'The deployment script works, I just need someone to explain what it does.' #DevOps #Reality",
    "Alert at 3am: High latency on service X.\nMe: Restart pods.\nAlerts resolve.\nMe: *goes back to sleep*\nSame alert at 4am: #SRE #OnCall #DevOps",
    "The DevOps food chain:\n- Developer: 'It works locally'\n- DevOps: 'It deploys to staging'\n- SRE: 'It's fine in prod'\n- Users: 'IT'S BROKEN' #DevOps #SRE",
    "My Terraform naming convention:\n- v1: 'test'\n- v2: 'prod'\n- v3: 'prod_real'\n- v4: 'prod_real_final'\n- v5: 'prod_real_final_dont_touch'\n- v6: *deletes everything and starts over* #Terraform",
    "Docker image sizes over time:\n- Before optimization: 2.4GB\n- After multi-stage build: 48MB\nMe explaining this to my team for 30 min: priceless #Docker #DevOps",
    "The CI pipeline is red.\nDeveloper: 'Probably just a flaky test, re-run it.'\n*re-runs 5 times*\nDeveloper: 'Probably just a flaky test.' #CICD #DevOps",
    "Kubernetes: I killed your pod because it was using too much memory.\nMe: But I needed that pod.\nKubernetes: You should have set resource limits.\nMe: ...fair. #Kubernetes #DevOps",
    "DevOps engineer salary negotiation:\nMe: I'd like a raise.\nHR: We offer competitive compensation.\nMe: I was on call 11 weekends this year.\nHR: We offer competitive compensation. #DevOps #SRE",
    "Me: I'll write the Ansible playbook real quick.\n*2 hours later*\n'- name: Install dependency for the dependency that installs the actual dependency' #Ansible #DevOps #IaC",
    "Tech debt: 'We'll fix it after launch.'\n6 months later: 'That's just how it works now.'\n2 years later: The intern who touched it is now the only person who understands it. #DevOps #TechDebt",
    "Explaining K8s to a non-tech friend:\nMe: It's like a datacenter... but it's software... that manages other software... that runs your software.\nFriend: So it's... magic? #Kubernetes",
    "The DevOps paradox: The better you are at your job, the more invisible your work becomes. No one notices the deployments that went fine. #SRE #DevOps",
    "Someone touched the Jenkins server 3 years ago and now nobody knows the password. The Jenkins server keeps running. Nobody looks at it. It's fine. This is fine. #DevOps #Jenkins",
    "My k8s cluster at 2am:\nPod: *CrashLoopBackOff*\nMe: Why are you restarting?\nPod: *CrashLoopBackOff*\nLogs: 'Error: Error'\nMe: Perfect, very helpful. #Kubernetes #SRE",
    "DevOps engineer joining a new company:\nDay 1: 'Interesting architecture.'\nDay 3: 'Some of this could be improved.'\nDay 7: 'Who wrote this Dockerfile?'\nDay 30: 'I have made a terrible mistake.' #DevOps",
    "CI/CD pipeline names as their actual behavior:\n- 'Fast Deploy': 23 minutes\n- 'Staging': Broken since Tuesday\n- 'Production': Last successful run: 6 months ago\n- 'Hotfix': We just FTP'd it #CICD #DevOps",
    "Current vibe: `kubectl get pods -A | grep -v Running | grep -v Completed`\nOutput: *entire cluster* #Kubernetes #SRE #OnCall",
    "Learning Kubernetes stages:\n1. Install\n2. Deploy hello-world\n3. Feel powerful\n4. Expose a service\n5. Question your life choices\n6. Read the docs properly\n7. Goto 5 #Kubernetes #DevOps",
    "The best comment in infrastructure code I've ever seen: `# Don't touch this. It works. Nobody knows why. Please.` #DevOps #IaC #LegacyCode",
    "Security team: We found critical vulnerabilities in your container images.\nDevOps: How many?\nSecurity: 847.\nDevOps: How many are exploitable?\nSecurity: 3.\nDevOps: Cool, we'll fix those 3. #DevSecOps",
    "Me, deploying at 4:55pm on Friday: This is fine. I understand the risks. I am a professional. I have tested this thoroughly.\n*Pager goes off at 5:01pm* #DevOps #CICD #SRE",
    "Cloud bill this month: $4,200\nIdentified cause: A dev left an r5.8xlarge running 'just for testing' since January. It is now June. #AWS #FinOps #CloudCost",
    "Them: Can you just quickly set up Kubernetes for our 3-service app?\nMe: ...I can, but I want to be clear about what 'quickly' means in this context. #Kubernetes #DevOps",
]

# ═════════════════════════════════════════════════════════════════════════════

ALL_SLOTS = [SLOT_0_PROJECT, SLOT_1_TIP, SLOT_2_HOTTAKE, SLOT_3_POLL, SLOT_4_MEME]


def pick_tweet(slot: int) -> str:
    pool = ALL_SLOTS[slot]
    day  = datetime.utcnow().timetuple().tm_yday
    idx  = (day - 1) % len(pool)
    tweet = pool[idx]

    # Unique suffix prevents X duplicate-content block
    stamp = datetime.utcnow().strftime("%d%b%H%M")  # e.g. 01Jun1747
    suffix = f" ~{stamp}"
    if len(tweet) + len(suffix) <= 280:
        tweet = tweet + suffix
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
    labels = ["Project Post", "DevOps Tip", "Hot Take", "Poll", "Relatable Meme"]
    print(f"[{datetime.utcnow().isoformat()}] Slot {SLOT} — {labels[SLOT]}")

    tweet_text = pick_tweet(SLOT)
    print(f"Selected tweet ({len(tweet_text)} chars):\n{tweet_text}\n")

    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    tweet_id = post_tweet(tweet_text)
    print(f"✅ Posted! https://x.com/rajaji2/status/{tweet_id}")


if __name__ == "__main__":
    main()
