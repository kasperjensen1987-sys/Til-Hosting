import sqlite3

class CVService:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS cv_experience (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, period TEXT, description TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_education (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, institution TEXT, period TEXT, description TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_volunteer (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, period TEXT, description TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_references (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_profile (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_skills (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, description TEXT)')
            
            if db.execute('SELECT COUNT(*) FROM cv_experience').fetchone()[0] == 0:
                self._seed_db(db)

    def _seed_db(self, db):
        # Profil data
        profile = [
            ('name', 'Kasper Groth Jensen'),
            ('title', 'Digital Specialist & Procesoptimering'),
            ('intro', 'Med et 12-tal i programmering og 20 års erfaring som teknisk bindeled, transformeres komplekse behov til automatiserede løsninger.'),
            ('address', '9210 Aalborg SØ'),
            ('phone', '+45 54334207'),
            ('email', 'kasperjensen1987@gmail.com'),
            ('linkedin', 'https://www.linkedin.com/in/kaspergrothjensen'),
            ('thingiverse', 'https://www.thingiverse.com/KgrothJensen/designs')
        ]
        db.executemany('INSERT INTO cv_profile (key, value) VALUES (?, ?)', profile)

        # Erhvervserfaring - Den fulde liste
        exp = [
            ('Design Data Specialist', 'Scandi Byg A/S', '2024 – 2025', 'Ansvarlig for teknisk implementering af softwaresystemer til modulbyggeri.'),
            ('BIM Udvikler / Tegner', 'Søgaard Stålbyg', '2023 – 2024', 'Automatisering af Tekla opsætninger og produktionsoptimering.'),
            ('Software tekniker & konsulent', 'BuildingPoint Scandinavia', '2021 – 2023', 'Teknisk support og rådgivning i Tekla Structures for hele Norden.'),
            ('BIM Specialist / Teknisk Designer', 'NIRAS', '2011 – 2021', 'Digital koordinering og 3D-modellering af store byggeprojekter.'),
            ('Teknisk Designer', 'Spæncom', '2006 – 2011', 'Konstruktion og automatisering af tegningsgenerering.')
        ]
        db.executemany('INSERT INTO cv_experience (title, company, period, description) VALUES (?, ?, ?, ?)', exp)

        # Uddannelse
        edu = [
            ('Videregående Python Programmering', 'Itucation', '2025', '6 ugers intensivt Full-stack forløb. Karakter: 12.'),
            ('Teknisk designer (EUD)', 'Aalborg tekniske Skole', '2003 - 2006', 'Fokus på CAD-konstruktion og IT.')
        ]
        db.executemany('INSERT INTO cv_education (title, institution, period, description) VALUES (?, ?, ?, ?)', edu)

        # Frivilligt & Referencer
        db.executemany('INSERT INTO cv_volunteer (title, period, description) VALUES (?, ?, ?)', [
            ('Bestyrelsesmedlem', 'Troopers for Charity', '2022 – Nu', 'Velgørenhed for syge børn.'),
            ('Uddannelsesudvalg', 'Teknisk Design, Aalborg', '2024 – 2026', 'Kvalitetssikring af uddannelsen.')
        ])
        db.executemany('INSERT INTO cv_references (quote) VALUES (?)', [
            ('”En organiseret og konstruktiv kollega.”',),
            ('”Hjælpsom, ansvarsfuld og imødekommende.”',)
        ])
        db.commit()

    def get_all_data(self):
        with self.get_db() as db:
            return {
                'profile': {row['key']: row['value'] for row in db.execute('SELECT * FROM cv_profile').fetchall()},
                'experience': db.execute('SELECT * FROM cv_experience').fetchall(),
                'education': db.execute('SELECT * FROM cv_education').fetchall(),
                'volunteer': db.execute('SELECT * FROM cv_volunteer').fetchall(),
                'references': db.execute('SELECT * FROM cv_references').fetchall()
            }