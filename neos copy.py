import praw
import pandas as pd
import datetime

posts = []
#use the subreddit name after the r/
name = 'SAP'
num_posts = 1000
reddit = praw.Reddit(client_id='COXKh7OTHx4rWgS4f6CkKg',
                     client_secret='25z-1pflYCJwGe9dfkLgwnsdaU0jsA',
                     user_agent='test')


subreddit_name = reddit.subreddit(name)

for post in subreddit_name.new(limit=num_posts):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
created = posts['created']
created = created.apply(lambda x: datetime.datetime.fromtimestamp(x))
posts['created'] = created

print(posts)
posts.to_csv("Posts.csv", index=True)

def count_posts_inlast_week(posts):
    last_week = datetime.datetime.now() - datetime.timedelta(days=7)
    return len(posts[posts['created'] > last_week])

print ("the post count in the last week is: ", count_posts_inlast_week(posts))
