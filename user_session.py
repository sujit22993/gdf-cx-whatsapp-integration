import uuid
import json
import pandas as pd
from tinydb import TinyDB, Query
import os
import logging

logger = logging.getLogger(__name__)

class UserSession:

    """
    Responsible to manage and store User-session data
    """

    def __init__(self) -> None:
        db_name = os.environ["SESSION_DB_NAME"]
        self.user = Query()
        '''
        Need to store file in /tmp for deployment over lambda as there is only read permission 
        at /var/task location. 
        Read more : https://repost.aws/questions/QUyYQzTTPnRY6_2w71qscojA/read-only-file-system-aws-lambda
        '''
        self.db = TinyDB(f"/tmp/{db_name}")

    def create_session(self, user_id: str, session_id: str) -> int:
        """
        Creating Session If not exist
        0 - Already Exist
        `some_id` - Index of the new entry
        """
        if not self.is_session(user_id):
            try:
                res = self.db.insert(
                    {"user_id": user_id, "session_id": session_id, "current_page": "NA"}
                )
                logger.info(f"New Session Created - {session_id}")
                return res
            except Exception as e:
                logger.error(f"Couldn't create Session - {e}")
                raise(e)
        return 0

    def is_session(self, user_id=None) -> bool:
        """
        Return : True => If there is a session ID exist for the user
        """
        result = self.db.search(self.user.user_id == user_id)
        if result:
            return True
        return False

    def get_session_id(self, user_id: str = None) -> str:
        """
        Return : Session ID => If there is a session ID exist for the user
        """
        result = self.db.search(self.user.user_id == user_id)
        if result:
            return result[0]["session_id"]
        return None

    def delete_session(self, user_id: str) -> int:
        if self.is_session(user_id):
            res = self.db.remove(self.user.user_id == user_id)
            return res
        return 0

    def get_session_data(self, user_id: str = None):
        """
        Session Data : For reporting purpose
        """
        if user_id:
            session_data = self.db.search(self.user.user_id == user_id)
            return session_data
        return self.db.all
