name: Post DevOps Tweet rajaji2 - 6 tweets per day

on:
  schedule:
    - cron: '30 2  * * *'   # Slot 0 — 08:00 IST
    - cron: '30 6  * * *'   # Slot 1 — 12:00 IST
    - cron: '30 8  * * *'   # Slot 2 — 14:00 IST
    - cron: '30 11 * * *'   # Slot 3 — 17:00 IST
    - cron: '30 13 * * *'   # Slot 4 — 19:00 IST
    - cron: '0  16 * * *'   # Slot 5 — 21:30 IST

  workflow_dispatch:
    inputs:
      slot:
        description: 'Slot (0=Project 1=Poll 2=Meme 3=Career 4=Motivational 5=Question)'
        required: true
        default: '0'
        type: choice
        options: ['0','1','2','3','4','5']

jobs:
  slot0:
    name: Slot 0 - Project Post (08:00 IST)
    if: github.event_name == 'schedule' && github.event.schedule == '30 2 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      "0"
        run: python post_tweet.py

  slot1:
    name: Slot 1 - Poll (12:00 IST)
    if: github.event_name == 'schedule' && github.event.schedule == '30 6 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      "1"
        run: python post_tweet.py

  slot2:
    name: Slot 2 - Meme (14:00 IST)
    if: github.event_name == 'schedule' && github.event.schedule == '30 8 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      "2"
        run: python post_tweet.py

  slot3:
    name: Slot 3 - Career Tip (17:00 IST)
    if: github.event_name == 'schedule' && github.event.schedule == '30 11 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      "3"
        run: python post_tweet.py

  slot4:
    name: Slot 4 - Motivational (19:00 IST)
    if: github.event_name == 'schedule' && github.event.schedule == '30 13 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      "4"
        run: python post_tweet.py

  slot5:
    name: Slot 5 - Community Question (21:30 IST)
    if: github.event_name == 'schedule' && github.event.schedule == '0 16 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      "5"
        run: python post_tweet.py

  manual:
    name: Manual trigger
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install tweepy
      - name: Post Tweet
        env:
          X_API_KEY:       ${{ secrets.X_API_KEY }}
          X_API_SECRET:    ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN:  ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_SECRET: ${{ secrets.X_ACCESS_SECRET }}
          CLAUDE_API_KEY:  ${{ secrets.CLAUDE_API_KEY }}
          TWEET_SLOT:      ${{ github.event.inputs.slot }}
        run: python post_tweet.py
