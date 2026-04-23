class Member:
    def __init__(self, id, full_name, gender, full_cpr_encrypted,
                 facebook, email, phone, address,
                 digital_post_exempt, digital_post_note,
                 child_check_status, child_check_note,
                 join_date, child_check_approved, child_check_renewal,
                 status, created_at):
        self.id = id
        self.full_name = full_name
        self.gender = gender
        self.full_cpr_encrypted = full_cpr_encrypted
        self.facebook = facebook
        self.email = email
        self.phone = phone
        self.address = address
        self.digital_post_exempt = digital_post_exempt
        self.digital_post_note = digital_post_note
        self.child_check_status = child_check_status
        self.child_check_note = child_check_note
        self.child_check_approved = child_check_approved
        self.child_check_renewal = child_check_renewal
        self.join_date = join_date
        self.status = status
        self.created_at = created_at