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
            db.execute('CREATE TABLE IF NOT EXISTS cv_volunteer (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, period TEXT, description TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_references (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_profile (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_skills (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, description TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_keywords (id INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_about (id INTEGER PRIMARY KEY AUTOINCREMENT, point TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_languages (id INTEGER PRIMARY KEY AUTOINCREMENT, language TEXT, level TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS cv_metadata (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, value TEXT)')
            
            if db.execute('SELECT COUNT(*) FROM cv_experience').fetchone()[0] == 0:
                self._seed_db(db)

    def _seed_db(self, db):
        # --- PROFIL & INTRO ---
        profile = [
            ('name', 'Kasper Groth Jensen'),
            ('title', 'Strategisk brobygger mellem IT, bygbarhed og mennesker'),
            ('intro', 'Jeg er en erfaren digital brobygger og teknisk konsulent med knap 20 års erfaring i at skabe sammenhæng mellem komplekse data, IT-systemer og de mennesker, der skal bruge dem. Min kernekompetence er procesoptimering; jeg fjerner friktion i organisationer ved at skabe smarte systemer og automatiseringer.'),
            ('address', 'Gustav Holms Vej 15, 9210 Aalborg SØ, Danmark'),
            ('phone', '+45 54334207'),
            ('email', 'kasperjensen1987@gmail.com'),
            ('linkedin', 'https://www.linkedin.com/in/kaspergrothjensen'),
            ('thingiverse', 'https://www.thingiverse.com/KgrothJensen/designs')
        ]
        db.executemany('INSERT INTO cv_profile (key, value) VALUES (?, ?)', profile)

        # --- OM MIG ---
        about = [
            ('Født og opvokset i Aalborg',), ('Har 2 teenagebørn (en af hver)',),
            ('Bor med min kæreste, Juline',), ('Elsker en god intellektuel udfordring',),
            ('Har altid ”ja-hatten” på',)
        ]
        db.executemany('INSERT INTO cv_about (point) VALUES (?)', about)

        # --- STIKORD ---
        keywords = [
            ('Udpræget brobygger',), ('Proaktiv problemløser',), ('Virksomhedens "go to person"',),
            ('Vellidt teamplayer',), ('Fagligt nysgerrig',), ('Struktureret og ansvarsfuld',),
            ('Stolt nørd',), ('Praktisk anlagt',), ('Altid imødekommende',)
        ]
        db.executemany('INSERT INTO cv_keywords (keyword) VALUES (?)', keywords)

        # --- SPROG & KØREKORT ---
        langs = [('Dansk', 'Modersmål / C2'), ('Engelsk', 'Avanceret / C1'), ('Tysk', 'Forståelse')]
        db.executemany('INSERT INTO cv_languages (language, level) VALUES (?, ?)', langs)
        db.execute('INSERT INTO cv_metadata (label, value) VALUES (?, ?)', ('Kørekort', 'B - Almindelig bil (egen bil)'))

        # --- KERNEKOMPETENCER ---
        skills = [
            ('Digital Transformation', 'Systemintegration og procesoptimering. Identificering og eliminering af ineffektive arbejdsgange.'),
            ('Data & Programmering', 'Avanceret brug af Python og SQL til databasearkitektur og behandling af komplekse datamængder.'),
            ('Rådgivning & Support', 'Seniorerfaring som "Trusted Advisor". Hotline-funktion og teknisk support i hele Norden.'),
            ('BIM & CAD Ekspertise', 'Ekspert i Tekla Structures, AutoCAD (20 år), Revit og forståelse for Dalux/Trimble Connect.'),
            ('Projektledelse', 'Udrulning af nye IT-værktøjer, teknisk dokumentation og sikring af høj brugeradoption.'),
            ('GIS & Forsyningsdata', 'Indgående kendskab til ledningsregistrering, DANDAS og GPS-opmåling i marken.')
        ]
        db.executemany('INSERT INTO cv_skills (category, description) VALUES (?, ?)', skills)

        # --- ERHVERVSERFARING (ALLE 11) ---
        exp = [
            ('Design Data Specialist', 'Scandi Byg, Løgstør', 'Aug 2024 – Apr 2025', 'Ansvarlig for teknisk implementering af HSBcad/HSBMake. Bindeled mellem tegnestue og produktion. Kvalitetssikrede software fra eksterne konsulenter.'),
            ('BIM Udvikler / Tegner', 'Søgaard Stålbyg', 'Aug 2023 – Jul 2024', 'Headhuntet til automatisering af Tekla-opsætninger. Omkonstruerede "kronen" på prestigebyggeriet "Posten" for fejlfri bygbarhed.'),
            ('Software tekniker & konsulent', 'BuildingPoint Scandinavia', 'Okt 2021 – Jul 2023', 'Teknisk rådgiver og supportspecialist for Tekla Structures i Norden. Trænede brugere og skræddersyede firmaopsætninger.'),
            ('Produktionstegner', 'Ambercon, Støvring', 'Dec 2020 – Sep 2021', '3D tegner og supporter under overgang til Tekla. Projekterede komplekse søjler til "Papirøen" i København.'),
            ('BIM Udvikler', 'Spæncom, Aalborg', 'Feb 2017 – Nov 2020', 'Kodede statiske beregninger i softwaren. International underviser for tegnestuer i Polen, Rumænien og Estland.'),
            ('Teknisk Designer', 'NIRAS, Aalborg', 'Jan 2012 – Jan 2017', 'GIS, ledningsregistrering (DANDAS) og GPS-opmåling. Oplæring af internationale praktikanter.'),
            ('Teknisk Designer (Udvikling)', 'PN Beslagfabrik', 'Sep 2009 – Aug 2011', 'Standardisering af sortimentet i 3D (CoCreate). Tæt dialog med produktionen om tekniske udfordringer.'),
            ('Teknisk Designer', 'DS Stålkonstruktion, Hobro', 'Jul 2008 – Feb 2009', 'Produktionstegninger af stålspær i AutoCAD 2D. (Stilling ophørt pga. finanskrise).'),
            ('Produktionsmedarbejder', 'PUMAC, Svenstrup', 'Sep 2007 – Jun 2008', 'Betjening af CNC-maskiner, laserskærere og revolverstansere på aftenhold. Hands-on maskinerfaring.'),
            ('Teknisk Designer & Operatør', 'Nytech, Vester Hassing', 'Jan 2007 – Aug 2007', 'Bindeled mellem design og udførelse. 3D konstruktion i SolidWorks og maskinprogrammering.'),
            ('Teknisk Designer Elev', 'Martin Professional', 'Sep 2004 – Jun 2006', 'Udlært inden for maskin- og produktionstegning af professionelt lysudstyr i PTA-afdelingen.')
        ]
        db.executemany('INSERT INTO cv_experience (title, company, period, description) VALUES (?, ?, ?, ?)', exp)

        # --- UDDANNELSE & KURSER (ALLE FRA DOKUMENTER) ---
        edu = [
            ('Teknisk designer (EUD)', 'Aalborg tekniske Skole', '2003 - 2006', 'Informationsteknologi, konstruktion, materialelære og 3D CAD.'),
            ('Videregående Python Programmering', 'Itucation', '2025', '6 ugers intensivt kursus (Karakter: 12). Webbaseret databaseudvikling med GDPR.'),
            ('HSB Make & Revit', 'HSBcad UK', '2025', 'Specialiseret træning i databasehåndtering og implementering.'),
            ('Power BI for begyndere', 'STI / Selvstudie', '2025', 'Datavisualisering og dashboards.'),
            ('Grafisk Facilitering', 'SimpleDraw', '2024', 'Træning i at visualisere komplekse arbejdsgange.'),
            ('Effektiv kommunikation', 'Teknologisk Institut', '2018', 'Konflikthåndtering og forandringsledelse.'),
            ('Tillidsrepræsentantuddannelsen', 'Teknisk Landsforbund', '2018', '12 dages uddannelse i forhandlingsteknik og arbejdsret.'),
            ('Revit Architecture 2017', 'CADskolen', '2016', 'Udvidet forståelse for BIM modellering.'),
            ('Grundkursus i afløbssystemer', 'Ferskvandscentret', '2012', 'Faglig viden om ledningsregistrering og spildevand.')
        ]
        db.executemany('INSERT INTO cv_education (title, institution, period, description) VALUES (?, ?, ?, ?)', edu)

        # --- FRIVILLIGT & TILLIDSHVERV (RETTET BINDINGS HER) ---
        vol = [
            ('Bestyrelsesmedlem & Frivillig', 'Troopers for Charity', '2022 – Nu', 'Besøg hos syge børn som Darth Maul. Tidligere bestyrelsesmedlem.'),
            ('Lokalt Uddannelsesudvalg', 'Teknisk Design, Aalborg', '2024 – 2026', 'Sikring af erhvervsuddannelsens kvalitet.'),
            ('Bestyrelsesmedlem', 'TL Nordjylland', '2022 – 2026', 'Interessevaretagelse frem til afgang marts 2026.'),
            ('Tillidsrepræsentant', 'Spæncom', '2018 – 2020', 'Trivsel og samarbejde på tværs af faggrupper.')
        ]
        db.executemany('INSERT INTO cv_volunteer (title, company, period, description) VALUES (?, ?, ?, ?)', vol)

        # --- REFERENCER ---
        refs = [('”En organiseret og konstruktiv kollega.”',), ('”Hjælpsom, ansvarsfuld og imødekommende.”',), 
                ('”Fagligt nysgerrig og grundig i opgaveløsning.”',), ('”En teamplayer med godt humør og stort engagement.”',)]
        db.executemany('INSERT INTO cv_references (quote) VALUES (?)', refs)
        db.commit()

    def get_all_cv_data(self):
        with self.get_db() as db:
            profile_rows = db.execute('SELECT key, value FROM cv_profile').fetchall()
            return {
                'profile': {row['key']: row['value'] for row in profile_rows},
                'about': db.execute('SELECT point FROM cv_about').fetchall(),
                'languages': db.execute('SELECT language, level FROM cv_languages').fetchall(),
                'metadata': {row['label']: row['value'] for row in db.execute('SELECT label, value FROM cv_metadata').fetchall()},
                'skills': db.execute('SELECT category, description FROM cv_skills').fetchall(),
                'keywords': db.execute('SELECT keyword FROM cv_keywords').fetchall(),
                'experience': db.execute('SELECT title, company, period, description FROM cv_experience').fetchall(),
                'education': db.execute('SELECT title, institution, period, description FROM cv_education').fetchall(),
                'volunteer': db.execute('SELECT title, company, period, description FROM cv_volunteer').fetchall(),
                'references': db.execute('SELECT quote FROM cv_references').fetchall()
            }

    def get_showcase(self):
        return [{
            'title': 'Eksamensprojekt: Medlemssystem',
            'grade': '12',
            'tech': 'Python, Flask, SQLite, Pandas',
            'description': 'Systemet er udviklet med Three-Tier Architecture, hvilket sikrer høj vedligeholdelsesgrad og klar separation af logik.',
            'code_sample': 'class MembersService:\n    def list_members(self, status=\'active\'):\n        query = \'SELECT * FROM members WHERE status = ?\'\n        return self.db.execute(query, [status])'
        }]