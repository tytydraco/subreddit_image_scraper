import hashlib
import os
import shutil
import sys
import urllib.request
import tempfile

import praw

# Argument check
if len(sys.argv) < 2:
    print('No subreddit specified.')
    sys.exit(1)

# Constants
SUBREDDIT = sys.argv[1]
ID = os.getenv('REDDIT_ID')
SECRET = os.getenv('REDDIT_SECRET')
OUT_DIR = 'img'

# Create output dir if missing
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

# Check if we are missing API key
if ID is None or SECRET is None:
    print('REDDIT_ID or REDDIT_SECRET is unset!')
    sys.exit(1)

# Create PRAW instance
reddit = praw.Reddit(
    client_id=ID,
    client_secret=SECRET,
    user_agent='scraper'
)

# Fetch top posts
subreddit = reddit.subreddit(SUBREDDIT)
hot_posts = subreddit.hot(limit=None)

tmpdir = tempfile.mkdtemp()
tmp_path = f'{tmpdir}/catrat_tmp'

# Go through all hot posts
for post in hot_posts:
    # Filter out non-images
    if post.domain != 'i.redd.it':
        continue

    # Store URL and image extension
    url = post.url
    ext = os.path.splitext(url)[1]

    # Download image
    urllib.request.urlretrieve(url, tmp_path)

    # Get MD5 hash of image contents
    with open(tmp_path, 'rb') as f:
        contents = f.read()
    hash_hex_digest = hashlib.md5(contents).hexdigest()

    # Copy temp file to our output directory
    new_file = f'{hash_hex_digest}{ext}'
    if not os.path.exists(new_file):
        shutil.copy(tmp_path, f'{OUT_DIR}/{new_file}')
        print(url)

# Remove temp file
os.remove(tmp_path)
