import sqlite3
from typing import Optional, List, Dict, Any

def _order_by_join_date_desc_sql() -> str:
    """Sortér dd-mm-YYYY som YYYY-mm-dd i SQLite"""
    return "(SUBSTR(join_date,7,4)||'-'||SUBSTR(join_date,4,2)||'-'||SUBSTR(join_date,1,2)) DESC"

class Db_Members:
    """
    DB-adgang members-struktur
    Kolonner (min.): id, full_name, gender, full_cpr_encrypted, facebook, email, phone, address,
    digital_post_exempt, digital_post_note, child_check_status, child_check_note,
    join_date, child_check_approved, child_check_renewal, status, created_at,
    leave_date (NULL), leave_reason (NULL)
    """
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        cur = self.connection.cursor()
        cur.execute("PRAGMA table_info(members)")
        cols = {r[1] for r in cur.fetchall()}
        if 'leave_date' not in cols:
            cur.execute("ALTER TABLE members ADD COLUMN leave_date TEXT NULL")
        if 'leave_reason' not in cols:
            cur.execute("ALTER TABLE members ADD COLUMN leave_reason TEXT NULL")
        self.connection.commit()
        cur.close()

    # Til stistikberegninger (aktiv/inaktiv)
    def count_by_status(self, status: str) -> int:
        cur = self.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM members WHERE status=?", (status,))
        n = cur.fetchone()[0] or 0
        cur.close()
        return n

    # Lister
    def list_members(self, status: Optional[str]) -> List[Dict[str, Any]]:
        cur = self.connection.cursor()
        ob = _order_by_join_date_desc_sql()
        if status in ("active", "inactive"):
            cur.execute(f"SELECT * FROM members WHERE status=? ORDER BY {ob}, full_name", (status,))
        else:
            cur.execute(f"SELECT * FROM members ORDER BY {ob}, full_name")
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    def get_member(self, member_id: int) -> Optional[Dict[str, Any]]:
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM members WHERE id=?", (member_id,))
        row = cur.fetchone()
        cur.close()
        return dict(row) if row else None

    def renewals_in_year(self, year: int) -> List[Dict[str, Any]]:
        cur = self.connection.cursor()
        # child_check_renewal er tekst i dd-mm-YYYY søger på årstal
        cur.execute(
            "SELECT * FROM members WHERE child_check_renewal LIKE ? ORDER BY full_name",
            (f"%-{year}",)
        )
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    # CRUD
    def insert_member(self, m) -> None:
        cur = self.connection.cursor()
        cur.execute(
            """INSERT INTO members
               (full_name, gender, full_cpr_encrypted,
                facebook, email, phone, address, digital_post_exempt,
                digital_post_note, child_check_status, child_check_note,
                join_date, child_check_approved, child_check_renewal,
                status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                m.full_name, m.gender, m.full_cpr_encrypted,
                m.facebook, m.email, m.phone, m.address, m.digital_post_exempt,
                m.digital_post_note, m.child_check_status, m.child_check_note,
                m.join_date, m.child_check_approved, m.child_check_renewal,
                m.status, m.created_at,
            )
        )
        self.connection.commit()
        cur.close()

    def update_member(self, member_id: int, m) -> None:
        cur = self.connection.cursor()
        cur.execute(
            """UPDATE members SET
                 full_name=?,
                 gender=?,
                 full_cpr_encrypted=?,
                 facebook=?,
                 email=?,
                 phone=?,
                 address=?,
                 digital_post_exempt=?,
                 digital_post_note=?,
                 child_check_status=?,
                 child_check_note=?,
                 join_date=?,
                 child_check_approved=?,
                 child_check_renewal=?,
                 status=?
               WHERE id=?""",
            (
                m.full_name, m.gender, m.full_cpr_encrypted,
                m.facebook, m.email, m.phone, m.address,
                m.digital_post_exempt, m.digital_post_note,
                m.child_check_status, m.child_check_note,
                m.join_date, m.child_check_approved, m.child_check_renewal,
                m.status, member_id,
            )
        )
        self.connection.commit()
        cur.close()

    def delete_member(self, member_id: int):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM members WHERE id=?", (member_id,))
        self.connection.commit()
        cur.close()

    # Status / udmeld
    def toggle_status(self, member_id: int) -> None:
        cur = self.connection.cursor()
        cur.execute("SELECT status FROM members WHERE id=?", (member_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return
        new_status = "inactive" if row["status"] == "active" else "active"
        cur.execute("UPDATE members SET status=? WHERE id=?", (new_status, member_id))
        self.connection.commit()
        cur.close()

    def set_inactive(self, member_id: int, leave_date: str, leave_reason: str):
        """
        Sætter medlem inaktivt og anonymiserer alle øvrige felter
        så kun (full_name, join_date, leave_date, leave_reason, status) bevares
        """
        cur = self.connection.cursor()
        cur.execute(
            """
            UPDATE members SET
                status = 'inactive',
                leave_date = ?,
                leave_reason = ?,
                -- Anonymisering / nulstilling af øvrige felter:
                gender = 'Ej angivet',
                full_cpr_encrypted = '',
                facebook = '',
                email = '',
                phone = '',
                address = '',
                digital_post_exempt = 0,
                digital_post_note = '',
                child_check_status = 'Ikke indhentet',
                child_check_note = '',
                child_check_approved = NULL,
                child_check_renewal = NULL
            WHERE id = ?
            """
                , (leave_date, leave_reason, member_id))
        self.connection.commit()
        cur.close()

    def reactivate(self, member_id: int) -> None:
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE members SET status='active', leave_date=NULL, leave_reason=NULL WHERE id=?",
            (member_id,)
        )
        self.connection.commit()
        cur.close()