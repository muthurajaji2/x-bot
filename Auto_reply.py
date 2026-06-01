#!/usr/bin/env python3
"""
Auto-reply to comments for @rajaji2
Runs every 2 hours via GitHub Actions
Checks recent mentions → Claude generates reply → posts it
Tracks replied tweet IDs in a local file to avoid double-replies
"""

import os
import json
import urllib.request
import urllib.error
import tweepy
from datetime import datetime, timezone, timedelta

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
X_API_KEY       = os.environ["X_API_KEY"]
X_API_SECRET    = os.environ["X_API_SECRET"]
X_ACCESS_TOKEN  = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]
CLAUDE_API_KEY  = os.environ["CLAUDE_API_KEY"]

# ── Config ────────────────────────────────────────────────────────────────────
MY_USERNAME     = "rajaji2"
REPLIED_FILE    = "replied_ids.json"   # tracked in repo to avoid double replies
MAX_REPLIES     = 10                   # max replies per run (avoid rate limits)

# ── Skip replying to these (bots, yourself) ───────────────────────────────────
SKIP_USERS = {MY_USERNAME, "twitterapi", "x"}


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def load_replied_ids() -> set:
    """Load set of tweet IDs we have already replied to."""
    if os.path.exists(REPLIED_FILE):
        with open(REPLIED_FILE) as f:
            data = json.load(f)
            return set(data.get("ids", []))
    return set()


def save_replied_ids(ids: set):
    """Save replied IDs — keep only last 1000 to avoid file bloat."""
    recent = list(ids)[-1000:]
    with open(REPLIED_FILE, "w") as f:
        json.dump({"ids": recent, "updated": datetime.utcnow().isoformat()}, f, indent=2)


def get_clients():
    client = tweepy.Client(
        consumer_key        = X_API_KEY,
        consumer_secret     = X_API_SECRET,
        access_token        = X_ACCESS_TOKEN,
        access_token_secret = X_ACCESS_SECRET,
        wait_on_rate_limit  = True,
    )
    return client


def get_my_user_id(client) -> str:
    me = client.get_me()
    return str(me.data.id)


# ═════════════════════════════════════════════════════════════════════════════
# Claude — generate reply
# ═════════════════════════════════════════════════════════════════════════════

def generate_reply(comment_text: str, commenter: str, original_tweet: str) -> str:
    prompt = (
        f"You are @rajaji2, a DevOps engineer on X (Twitter) with an active community.\n"
        f"Someone replied to one of your tweets. Write a friendly, helpful, and genuine reply.\n\n"
        f"Your original tweet:\n{original_tweet}\n\n"
        f"Reply from @{commenter}:\n{comment_text}\n\n"
        f"Guidelines:\n"
        f"- Keep it under 240 characters\n"
        f"- Be conversational and human, not robotic\n"
        f"- If it's a question about DevOps/cloud/CI-CD, give a brief helpful answer\n"
        f"- If it's positive/supportive, thank them genuinely\n"
        f"- If it's a debate/hot take, engage thoughtfully\n"
        f"- Don't start with 'Hey' or 'Hi' every time — vary your openings\n"
        f"- Do NOT use hashtags in replies\n"
        f"- Never be promotional or salesy\n\n"
        f"Return ONLY the reply text. No quotes. No explanation."
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
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print(f"[{datetime.utcnow().isoformat()}] Auto-reply job starting...")

    client      = get_clients()
    my_user_id  = get_my_user_id(client)
    replied_ids = load_replied_ids()

    print(f"   My user ID  : {my_user_id}")
    print(f"   Already replied to {len(replied_ids)} tweets")

    # Fetch mentions from the last 2 hours
    since = datetime.now(timezone.utc) - timedelta(hours=2)

    mentions = client.get_users_mentions(
        id               = my_user_id,
        start_time       = since,
        max_results      = 20,
        expansions       = ["author_id", "in_reply_to_user_id", "referenced_tweets.id"],
        tweet_fields     = ["created_at", "text", "in_reply_to_user_id", "referenced_tweets"],
        user_fields      = ["username"],
    )

    if not mentions.data:
        print("   No new mentions found. Done.")
        return

    # Build a lookup: tweet_id → tweet text (for referenced/original tweets)
    ref_tweets = {}
    if mentions.includes and "tweets" in mentions.includes:
        for t in mentions.includes["tweets"]:
            ref_tweets[str(t.id)] = t.text

    # Build a lookup: user_id → username
    users = {}
    if mentions.includes and "users" in mentions.includes:
        for u in mentions.includes["users"]:
            users[str(u.id)] = u.username

    reply_count = 0

    for mention in mentions.data:
        tweet_id    = str(mention.id)
        author_id   = str(mention.author_id) if hasattr(mention, "author_id") else "unknown"
        commenter   = users.get(author_id, "someone")
        comment_txt = mention.text

        # Skip if already replied
        if tweet_id in replied_ids:
            print(f"   ⏭  Already replied to {tweet_id}")
            continue

        # Skip our own tweets and known bots
        if commenter.lower() in SKIP_USERS:
            print(f"   ⏭  Skipping @{commenter} (self or bot)")
            replied_ids.add(tweet_id)
            continue

        # Get the original tweet text this is replying to
        original = "a DevOps tweet"
        if mention.referenced_tweets:
            for ref in mention.referenced_tweets:
                if ref.type == "replied_to":
                    original = ref_tweets.get(str(ref.id), "a DevOps tweet")
                    break

        print(f"\n   💬 @{commenter}: {comment_txt[:80]}...")
        print(f"   🔗 Original: {original[:60]}...")

        try:
            reply_text = generate_reply(comment_txt, commenter, original)
            print(f"   🤖 Reply: {reply_text}")

            # Post the reply
            client.create_tweet(
                text                    = reply_text,
                in_reply_to_tweet_id    = tweet_id,
            )
            print(f"   ✅ Replied to tweet {tweet_id}")

            replied_ids.add(tweet_id)
            reply_count += 1

        except Exception as e:
            print(f"   ❌ Failed to reply to {tweet_id}: {e}")
            replied_ids.add(tweet_id)   # mark as done to avoid retrying

        if reply_count >= MAX_REPLIES:
            print(f"\n   ⚠️  Hit max replies ({MAX_REPLIES}) for this run")
            break

    save_replied_ids(replied_ids)
    print(f"\n✅ Done — sent {reply_count} replies this run")


if __name__ == "__main__":
    main()
