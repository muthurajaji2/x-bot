# 🐦 X Auto-Poster for @rajaji2
> DevOps / CI-CD / Cloud niche · 5 tweets/day · Powered by Claude AI + GitHub Actions

---

## 📁 File Structure

```
rajaji2-x-bot/
├── .github/
│   └── workflows/
│       └── tweet.yml       ← GitHub Actions schedule
├── post_tweet.py           ← Main script (Claude + X API)
├── requirements.txt
└── README.md
```

---

## 🚀 Setup (One-time, ~15 minutes)

### Step 1 — Get X API Keys

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign in with **@rajaji2**
3. Create a new **Project** → Create an **App** inside it
4. Set App permissions to **Read and Write**
5. Go to **Keys and Tokens** tab → copy all 4 values:
   - `API Key`
   - `API Key Secret`
   - `Access Token`  ← make sure it says "Read and Write"
   - `Access Token Secret`

### Step 2 — Get Claude API Key

1. Go to https://console.anthropic.com
2. Create account / sign in
3. Go to **API Keys** → Create new key
4. Copy the key (starts with `sk-ant-...`)

### Step 3 — Create GitHub Repo

```bash
# Create a new private repo on github.com first, then:
git init
git remote add origin https://github.com/rajaji2/x-bot.git  # your repo URL
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Step 4 — Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 5 secrets:

| Secret Name       | Value                          |
|-------------------|-------------------------------|
| `X_API_KEY`       | Your X API Key                |
| `X_API_SECRET`    | Your X API Key Secret         |
| `X_ACCESS_TOKEN`  | Your X Access Token           |
| `X_ACCESS_SECRET` | Your X Access Token Secret    |
| `CLAUDE_API_KEY`  | Your Anthropic API Key        |

### Step 5 — Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. Done! ✅

---

## ⏰ Tweet Schedule (IST)

| Time (IST) | Type            | Example Content                              |
|------------|-----------------|----------------------------------------------|
| 8:00 AM    | 🖼️ Project Post  | "Build a GitHub Actions CI pipeline today..." |
| 11:00 AM   | 💡 DevOps Tip    | "Use --cache-from in Docker builds to..."    |
| 2:00 PM    | 🔥 Hot Take      | "Helm is just YAML with more YAML..."        |
| 5:00 PM    | 📊 Poll          | "What's your Kubernetes pain point? 🧵"      |
| 9:00 PM    | 😂 Relatable     | "It's Friday 5pm. Pipeline is red. Classic." |

---

## 🧪 Test Manually

Run a specific slot locally:
```bash
export X_API_KEY=...
export X_API_SECRET=...
export X_ACCESS_TOKEN=...
export X_ACCESS_SECRET=...
export CLAUDE_API_KEY=...
export TWEET_SLOT=0   # 0-4

pip install -r requirements.txt
python post_tweet.py
```

Or trigger from GitHub UI:
→ Actions → "Post DevOps Tweet" → Run workflow → pick slot 0-4

---

## 💰 Cost Estimate

| Service        | Usage              | Cost/month |
|----------------|--------------------|------------|
| GitHub Actions | ~150 runs/month    | **Free**   |
| X API Basic    | 1,500 tweets limit | **Free**   |
| Claude API     | ~150 calls × ~300 tokens | **~$0.50** |

**Total: ~$0.50/month**

---

## 🔧 Customization

Edit `post_tweet.py` to change:
- `PROJECTS` list — add your own DevOps projects
- `TOPICS` list — add topics you care about
- `TWEET_TYPES` prompts — adjust tone/style per slot
