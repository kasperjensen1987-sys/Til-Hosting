from werkzeug.security import check_password_hash
from storage.db_users import Db_Users
class AuthService:
    def __init__(self, db_path: str):
        self._db = Db_Users(db_path)
    def verify(self, username: str, password: str):
        row = self._db.get_by_username(username)
        if not row: return None
        return row if check_password_hash(row['password_hash'], password) else None