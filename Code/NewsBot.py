import praw

def GetRedditPosts():
    reddit = praw.Reddit(
        client_id="GGWxQCbPKwvhtSaDQyBJVA",
        client_secret="TxmGWaKjFX2sBMlES3b-A4FwtcPXxQ",
        user_agent="your_user_agent"
    )

    subreddit = reddit.subreddit("pennystocks")
    for post in subreddit.hot(limit=10):
        print(post.title, post.score, post.selftext, post.url)
        print("/n")