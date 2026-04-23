from datetime import datetime, date
from flask import current_app
from typing import Optional, Dict, Any, List
import base64
import hashlib
from models.member import Member
from storage.db_members import Db_Members

# Kryptering af sidste 4 cifre
def _key_bytes() -> bytes:
    secret = current_app.config.get('SECRET_KEY', 'dev-change-me')
    return hashlib.sha256(secret.encode('utf-8')).digest()

def encrypt_last4(last4: str) -> str:
    kb = _key_bytes()
    data = (last4 or '').encode('utf-8')
    enc = bytes([data[i] ^ kb[i % len(kb)] for i in range(len(data))])
    return base64.urlsafe_b64encode(enc).decode('utf-8')

def decrypt_last4(token: str) -> str:
    kb = _key_bytes()
    try:
        t = (token or '').encode('utf-8')
        padding = b'=' * ((4 - (len(t) % 4)) % 4)
        enc = base64.urlsafe_b64decode(t + padding)
        dec = bytes([enc[i] ^ kb[i % len(kb)] for i in range(len(enc))]).decode('utf-8')
        if dec.isdigit() and len(dec) == 4:
            return dec
    except Exception:
        pass
    return '****'

# CPR-hjælpere
def _split_full_cpr(full_cpr_encrypted: str) -> tuple[str, str]:
    """
    Forventer lagret format: 'dd-mm-YYYY-<encrypted_last4>'
    Returnerer (birth, token) eller ('','') hvis ugyldigt
    """
    s = (full_cpr_encrypted or '').strip()
    if len(s) >= 15 and s[2] == '-' and s[5] == '-' and s[10] == '-':
        return s[:10], s[11:]
    return '', ''

def cpr_display(full_cpr_encrypted: str, show_last4: bool = False) -> str:
    """
    Viser dd-mm-yy-xxxx
    """
    birth, token = _split_full_cpr(full_cpr_encrypted)
    if not birth:
        return '-'
    dd, mm, yyyy = birth[:2], birth[3:5], birth[6:10]
    yy = yyyy[-2:]
    last4 = decrypt_last4(token) if (show_last4 and token) else '****'
    return f"{dd}-{mm}-{yy}-{last4}"

def cpr_display_compact(full_cpr_encrypted: str, show_last4: bool = False) -> str:
    """
    Viser CPR som ddmmyy-xxxx
    Hvis show_last4=True vises de sidste 4, ellers ****
    """
    birth, token = _split_full_cpr(full_cpr_encrypted)
    if not birth:
        return '-'
    try:
        dd, mm, yyyy = birth[:2], birth[3:5], birth[6:10]
        if not (dd.isdigit() and mm.isdigit() and yyyy.isdigit()):
            return '-'
        yy = yyyy[-2:]
    except Exception:
        return '-'
    last4 = decrypt_last4(token) if (show_last4 and token) else '****'
    return f"{dd}{mm}{yy}-{last4}"

def _parse_birthdate(full_cpr_encrypted: str):
    birth, _ = _split_full_cpr(full_cpr_encrypted)
    if not birth:
        return None
    try:
        return datetime.strptime(birth, '%d-%m-%Y').date()
    except Exception:
        return None

def age_from_full_cpr(full_cpr_encrypted: str):
    bd = _parse_birthdate(full_cpr_encrypted)
    if not bd:
        return None
    today = date.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

# Øvrige hjælpere
def _normalize_gender(value: str) -> str:
    v = (value or '').strip()
    return v if v in ('Mand', 'Kvinde', 'Andet', 'Ej angivet') else 'Ej angivet'

def _order_key_join_date(row: Dict[str, Any]) -> str:
    jd = (row.get('join_date') or '').strip()  # dd-mm-YYYY
    if len(jd) == 10 and jd[2] == '-' and jd[5] == '-':
        return jd[6:10] + '-' + jd[3:5] + '-' + jd[0:2]
    return ''

# Service
class MembersService:
    def __init__(self, db_path: str):
        self._db = Db_Members(db_path)

    # aggregates
    def count_by_status(self, status: str) -> int:
        return self._db.count_by_status(status)

    # hjælper
    def count_active(self) -> int:
        return self.count_by_status('active')

    def count_inactive(self) -> int:
        return self.count_by_status('inactive')

    # list / get
    def list_members(self, status: Optional[str]):
        return self._db.list_members(status)

    def get_member(self, member_id: int):
        return self._db.get_member(member_id)

    # Opret
    def create_member(self, form):
        full_name = (form.get('full_name', '') or '').strip()
        gender = _normalize_gender(form.get('gender', 'Ej angivet'))
        full_cpr_input = (form.get('full_cpr', '') or '').strip()  # 'dd-mm-yyyy-xxxx'
        facebook = (form.get('facebook', '') or '').strip()
        email = (form.get('email', '') or '').strip()
        phone = (form.get('phone', '') or '').strip()
        address = (form.get('address', '') or '').strip()
        digital_post_exempt = 1 if form.get('digital_post_exempt') == 'on' else 0
        digital_post_note = (form.get('digital_post_note', '') or '').strip()
        join_date = (form.get('join_date', '') or '').strip()
        child_approved = (form.get('child_check_approved', '') or '').strip() or None
        child_check_status = (form.get('child_check_status', '') or '').strip() or 'Ikke indhentet'
        child_check_note = (form.get('child_check_note', '') or '').strip()
        status = (form.get('status', 'active') or 'active').strip() or 'active'

        # CPR-validering og lagringsformat
        if not (len(full_cpr_input) >= 15 and full_cpr_input[2] == '-' and full_cpr_input[5] == '-' and full_cpr_input[10] == '-'):
            return False, "Ugyldigt CPR-format. Brug dd-mm-yyyy-xxxx."
        birth = full_cpr_input[:10]
        last4_plain = full_cpr_input[11:15]
        if not (last4_plain.isdigit() and len(last4_plain) == 4):
            return False, "Ugyldigt CPR-format (sidste 4 skal være tal)."
        full_cpr_encrypted = f"{birth}-{encrypt_last4(last4_plain)}"

        # Under 18 er Undtaget
        age = age_from_full_cpr(full_cpr_encrypted) or 0
        if age < 18:
            child_check_status = 'Undtaget'

        # +2 år ved godkendelse
        child_renewal = None
        if child_approved:
            try:
                d = datetime.strptime(child_approved, '%d-%m-%Y').date()
                child_renewal = d.replace(year=d.year + 2).strftime('%d-%m-%Y')
            except Exception:
                child_renewal = None

        # Krav
        if not full_name:
            return False, "Fulde Navn er påkrævet."
        if not join_date:
            return False, "Indmeldelsesdato er påkrævet."
        if not email:
            return False, "Email er påkrævet."

        m = Member(
            None, full_name, gender, full_cpr_encrypted,
            facebook, email, phone, address, digital_post_exempt, digital_post_note,
            child_check_status, child_check_note, join_date, child_approved, child_renewal,
            status, datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        )
        self._db.insert_member(m)
        return True, "Medlem oprettet"

    # Opdater
    def update_member(self, member_id: int, form):
        row = self._db.get_member(member_id)
        if not row:
            return False, "Medlem ikke fundet."

        full_name = (form.get('full_name', '') or '').strip() or row['full_name']
        gender = _normalize_gender(form.get('gender', row.get('gender')))
        full_cpr_input = (form.get('full_cpr', '') or '').strip()  # valgfrit – kun hvis CPR ændres
        facebook = (form.get('facebook', row.get('facebook')) or '').strip()
        email = (form.get('email', row.get('email')) or '').strip()
        phone = (form.get('phone', row.get('phone')) or '').strip()
        address = (form.get('address', row.get('address')) or '').strip()
        digital_post_exempt = 1 if form.get('digital_post_exempt') == 'on' else int(row.get('digital_post_exempt') or 0)
        digital_post_note = (form.get('digital_post_note', row.get('digital_post_note')) or '').strip()
        join_date = (form.get('join_date', row.get('join_date')) or '').strip()
        child_approved = (form.get('child_check_approved', row.get('child_check_approved')) or '').strip() or None
        child_check_status = (form.get('child_check_status', row.get('child_check_status')) or '').strip() or 'Ikke indhentet'
        child_check_note = (form.get('child_check_note', row.get('child_check_note')) or '').strip()
        status = (form.get('status', row.get('status') or 'active') or 'active').strip() or 'active'

        # CPR
        if full_cpr_input:
            if not (len(full_cpr_input) >= 15 and full_cpr_input[2] == '-' and full_cpr_input[5] == '-' and full_cpr_input[10] == '-'):
                return False, "Ugyldigt CPR-format. Brug dd-mm-yyyy-xxxx."
            birth = full_cpr_input[:10]
            last4_plain = full_cpr_input[11:15]
            if not (last4_plain.isdigit() and len(last4_plain) == 4):
                return False, "Ugyldigt CPR-format (sidste 4 skal være tal)."
            full_cpr_encrypted = f"{birth}-{encrypt_last4(last4_plain)}"
        else:
            full_cpr_encrypted = row.get('full_cpr_encrypted')

        # Under 18 er Undtaget
        age = age_from_full_cpr(full_cpr_encrypted) or 0
        if age < 18:
            child_check_status = 'Undtaget'

        # +2 år ved godkendelse
        child_renewal = None
        if child_approved:
            try:
                d = datetime.strptime(child_approved, '%d-%m-%Y').date()
                child_renewal = d.replace(year=d.year + 2).strftime('%d-%m-%Y')
            except Exception:
                child_renewal = None

        m = Member(
            member_id, full_name, gender, full_cpr_encrypted,
            facebook, email, phone, address, digital_post_exempt, digital_post_note,
            child_check_status, child_check_note, join_date, child_approved, child_renewal,
            status, datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        )
        self._db.update_member(member_id, m)
        return True, "Medlem opdateret"

    # Slet (returnerer ok, besked)
    def delete_member(self, member_id: int):
        """
        Sletter et medlem og returnerer True hvis slettet
        Falsehvis ikke fundet
        """
        row = self._db.get_member(member_id)
        if not row:
            return False, "Medlem ikke fundet."
        self._db.delete_member(member_id)
        return True, "Medlem slettet."

    # Status
    def toggle_status(self, member_id: int):
        self._db.toggle_status(member_id)

    def set_inactive(self, member_id: int, leave_date: str, leave_reason: str):
        self._db.set_inactive(member_id, leave_date, leave_reason)

    def reactivate(self, member_id: int):
        self._db.reactivate(member_id)

    # Fornyelser
    def renewals_in_year(self, year: int):
        return self._db.renewals_in_year(year)

    # alias hvis app.py kalder .renewals
    def renewals(self, year: int):
        return self.renewals_in_year(year)

    # Filter Under 18
    def filter_age(self, min_age: Optional[int] = None, max_age: Optional[int] = None, group: Optional[str] = None):
        rows = self._db.list_members('active')
        today = date.today()
        filtered: List[Dict[str, Any]] = []
        for r in rows:
            bd = _parse_birthdate(r.get('full_cpr_encrypted'))
            if not bd:
                continue
            years = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if group == 'under18':
                if years < 18:
                    filtered.append(r)
            else:
                if (min_age is None or years >= min_age) and (max_age is None or years <= max_age):
                    filtered.append(r)
        return sorted(filtered, key=_order_key_join_date, reverse=True)