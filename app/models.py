from flask_login import UserMixin
from bson.objectid import ObjectId

from .extensions import mongo, login_manager

class User(UserMixin):
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.username = doc.get("username")
        self.email = doc.get("email")
        self.display_name = doc.get("display_name", self.username)

    @staticmethod
    def from_doc(doc):
        return User(doc) if doc else None
    
    @staticmethod
    def find_by_id(user_id: str):
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except Exception:
                return None
        doc = mongo.db.users.find_one({"_id": user_id})
        return User.from_doc(doc)

    @staticmethod
    def find_by_username_or_email(identifier: str):
        doc = mongo.db.users.find_one(
            {"$or": [{"username": identifier}, {"email": identifier}]}
        )
        return User.from_doc(doc)
    
    @staticmethod
    def create(username: str, email: str, password_hash: str):
        doc={
                "username": username,
                "email": email,
                "password_hash":password_hash
            }
        result = mongo.db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return User.from_doc(doc)


@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)