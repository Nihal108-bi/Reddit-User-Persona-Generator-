
import os
import logging
from typing import List, Dict, Tuple, Optional
import praw
from prawcore.exceptions import NotFound
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ACTIVITY_LIMIT = 100

class RedditClient:
    def __init__(self):
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
                read_only=True,
            )
            self.reddit.user.me()
            logging.info("✅ Reddit client initialized successfully.")
        except Exception as e:
            logging.error(f"❌ Failed to initialize Reddit client: {e}")
            raise

    def get_user(self, username: str) -> Optional[Tuple[praw.models.Redditor, Optional[str]]]:
        """
        Retrieves a Redditor instance and their avatar URL.
        Returns a tuple of (user_object, avatar_url) or None if not found.
        """
        try:
            user = self.reddit.redditor(username)
            
            avatar_url = getattr(user, 'icon_img', None)
            return user, avatar_url
        except NotFound:
            logging.error(f"❌ Reddit user '{username}' not found. The user may be banned or have deleted their account.")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred while fetching user '{username}': {e}")
            logging.error("This could be due to temporary Reddit API issues or rate-limiting. Please wait a few minutes and try again.")
            return None

    def get_user_activity(self, user) -> List[Dict[str, str]]:
        activity = []
        logging.info(f"Fetching up to {ACTIVITY_LIMIT} comments and posts for u/{user.name}...")
        try:
            for comment in user.comments.new(limit=ACTIVITY_LIMIT):
                activity.append({
                    "type": "comment",
                    "content": comment.body,
                    "permalink": f"https://www.reddit.com{comment.permalink}",
                })
            for post in user.submissions.new(limit=ACTIVITY_LIMIT):
                activity.append({
                    "type": "post",
                    "content": f"Title: {post.title}\nBody: {post.selftext}",
                    "permalink": f"https://www.reddit.com{post.permalink}",
                })
        except Exception as e:
            logging.warning(f"Could not fetch all activity for u/{user.name}: {e}")
        return activity