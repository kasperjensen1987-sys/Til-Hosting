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
            ('intro', 'Jeg er en erfaren digital brobygger og teknisk konsulent med knap 20 års erfaring i at skabe sammenhæng mellem komplekse data, IT-systemer og de mennesker, der skal bruge dem[cite: 1, 3]. Min kernekompetence er procesoptimering; jeg fjerner friktion i organisationer ved at skabe smarte systemer og automatiseringer, der gør hverdagen nemmere for mine kolleger og kunder[cite: 1, 3].'),
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

        # --- STIKORD OM MIG ---
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

        # --- TEKNISKE KERNEKOMPETENCER ---
        skills = [
            ('Softwareudvikling & Data', 'Stærke kompetencer i Python (videregående niveau) og SQL. Jeg anvender objektorienteret programmering og databasemodellering til at håndtere store tekniske datasæt[cite: 3].'),
            ('Specialist CAD & BIM', 'Ekspert i Tekla Structures, AutoCAD (20 år) og Revit Architecture. Unik evne til at skabe integration mellem 3D-modeller og produktionsdata[cite: 3].'),
            ('Systemoptimering', 'Teknisk specialist i implementering af systemer som HSBMake. Erfaring med at overtage og fuldføre komplekse udrulninger fra eksterne konsulenter[cite: 3].'),
            ('Automation', 'Udvikling af automatiserede funktioner og scripts til procesoptimering. Fjerner manuelle arbejdsgange gennem intelligent kode[cite: 3].'),
            ('IT-Infrastruktur & ERP', 'Erfaring med drift og fejlfinding i komplekse miljøer, herunder SAP, samt fuld hardware- og software-opsætning[cite: 3].'),
            ('Teknisk Rådgivning', 'Seniorerfaring som "Trusted Advisor" i hele Norden. Ekspert i teknisk it-support, undervisning og onboarding[cite: 3].')
        ]
        db.executemany('INSERT INTO cv_skills (category, description) VALUES (?, ?)', skills)

        # --- ERHVERVSERFARING (VERIFICERET MOD ALLE KILDER) ---
        exp = [
            ('Design Data Specialist', 'Scandi Byg, Løgstør', 'Aug 2024 – Apr 2025', 
             'Ansvarlig for teknisk og menneskelig implementering af HSBcad/HSBMake til Revit og AutoCAD. '
             'Fungerede som bindeled mellem tegnestue og produktion. Kvalitetssikrede softwarens reelle formåen og udarbejdede udrulningsplan[cite: 1, 3].'),
            
            ('BIM Udvikler / Tegner', 'Søgaard Stålbyg, Skive (Remote)', 'Aug 2023 – Jul 2024', 
             'Headhuntet direkte fra konsulentrolle. Udviklede og automatiserede Tekla-opsætninger. '
             'Omkonstruerede "kronen" på projektet "Posten" i København for at sikre fejlfri bygbarhed direkte i softwaren[cite: 1, 3].'),
            
            ('Software tekniker & konsulent', 'BuildingPoint Scandinavia (Remote)', 'Okt 2021 – Jul 2023', 
             'Teknisk rådgiver og supportspecialist for Tekla Structures i Norden. '
             'Trænede brugere fra basis- til avanceret niveau og blev udlejet som specialist til komplekse kundeprojekter[cite: 1, 3].'),
            
            ('Produktionstegner', 'Ambercon, Støvring', 'Dec 2020 – Sep 2021', 
             '3D tegner og intern supporter i et komplekst produktionsmiljø. '
             'Fungerede som teknisk support for nye brugeres overgang fra AutoCAD 3D til Tekla Structures i forbindelse med projektering af "Papirøen"[cite: 1, 3].'),
            
            ('BIM Udvikler', 'Spæncom, Aalborg', 'Feb 2017 – Nov 2020', 
             'Udviklede funktioner og kodede statiske beregninger direkte i softwaren for at reducere tegnetid. '
             'International underviser for tegnestuer i Danmark, Polen, Rumænien og Estland[cite: 1, 3].'),
            
            ('Teknisk Designer', 'NIRAS, Aalborg', 'Jan 2012 – Jan 2017', 
             'Håndterede ledningsregistrering (DANDAS), 3D modellering og GPS-opmåling i marken. '
             'Ansvarlig for oplæring af internationale udvekslingsstuderende og praktikanter[cite: 1, 3].'),
            
            ('Teknisk Designer (Udvikling)', 'PN Beslagfabrik, Brønderslev', 'Sep 2009 – Aug 2011', 
             'Modellerede og standardiserede dokumentation for hele sortimentet i CoCreate uden forudgående træning. '
             'Tæt dialog med produktionen for at sikre gnidningsfri fremstilling[cite: 1, 3].'),
            
            ('Teknisk Designer', 'DS Stålkonstruktion, Hobro', 'Jul 2008 – Feb 2009', 
             'Udarbejdelse af præcise produktions- og arbejdstegninger af stålspær til store stålhaller i AutoCAD 2D[cite: 1, 3].'),
            
            ('Produktionsmedarbejder', 'PUMAC, Svenstrup', 'Sep 2007 – Jun 2008', 
             'Betjente CNC-maskiner, laserskærere og revolverstansere på aftenhold. '
             'Opbyggede den praktiske forståelse for produktionsmiljøet, som i dag danner grundlaget for mit IT-arbejde[cite: 1, 3].'),
            
            ('Teknisk Designer & Maskinoperatør', 'Nytech, Vester Hassing', 'Jan 2007 – Aug 2007', 
             'Bindeled mellem design og udførelse. Udarbejdede 3D-grundlag i SolidWorks og '
             'programmerede/betjente selvstændigt laserskærere og revolverstansere[cite: 1, 3].'),
            
            ('Teknisk Designer Elev', 'Martin Professional, Frederikshavn', 'Sep 2004 – Jun 2006', 
             'Udlært inden for maskin- og produktionstegning i den Produktionstekniske Afdeling (PTA). '
             'Udarbejdede styklister og løste samleudfordringer i tæt samarbejde med ingeniører[cite: 1, 3].')
        ]
        db.executemany('INSERT INTO cv_experience (title, company, period, description) VALUES (?, ?, ?, ?)', exp)

        # --- UDDANNELSE & KURSER ---
        edu = [
            ('Teknisk designer (EUD)', 'Aalborg tekniske Skole', '2003 - 2006', 
             'Omfatter IT, beregning, materialelære, 3D-animation og teknisk dokumentation[cite: 1, 3].'),
            ('Videregående Python Programmering (Karakter: 12)', 'Itucation', '2025', 
             'Intensivt kursus med fokus på Flask, SQLite og Full-stack udvikling. Udviklede webbaseret medlemsdatabase[cite: 1, 3].'),
            ('HSB Make & HSB on Revit', 'HSBcad UK', '2025', 
             'Specialiseret træning i databasehåndtering og implementering direkte hos softwareudviklerne[cite: 1, 3].'),
            ('Power BI for begyndere', 'STI / Selvstudie', '2025', 
             'Fokus på datavisualisering og evnen til at omsætte rå data til forretningsværdi[cite: 1, 3].'),
            ('Tillidsrepræsentantuddannelsen', 'Teknisk Landsforbund', '2018', 
             'Fokus på forhandlingsteknik, arbejdsret, trivsel og konfliktløsning[cite: 1, 3].'),
            ('Effektiv kommunikation', 'Teknologisk Institut', '2018', 
             'Værktøjer til konflikthåndtering, forandringsledelse og tværfaglig kommunikation[cite: 1, 3].')
        ]
        db.executemany('INSERT INTO cv_education (title, institution, period, description) VALUES (?, ?, ?, ?)', edu)

        # --- FRIVILLIGT & TILLIDSHVERV ---
        vol = [
            ('Bestyrelsesmedlem & Frivillig', 'Troopers for Charity', '2022 – Nu', 
             'Besøg hos syge børn som karakteren Darth Maul. Skaber magiske frirum i svære situationer[cite: 1, 3].'),
            ('Lokalt Uddannelsesudvalg', 'Teknisk Design, Aalborg', '2024 – 2026', 
             'Udpeget medlem med fokus på at sikre kvaliteten og fremtiden for erhvervsuddannelsen[cite: 1, 3].'),
            ('Bestyrelsesmedlem', 'TL Nordjylland', '2022 – 2026', 
             'Organisatorisk arbejde og medlemsinteresser frem til planlagt afgang marts 2026[cite: 1, 3].'),
            ('Tillidsrepræsentant', 'Spæncom', '2018 – 2020', 
             'Fokus på trivsel, kommunikation og samarbejde på tværs af faggrupper[cite: 1, 3].')
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
            'description': 'Systemet er udviklet med Three-Tier Architecture, hvilket sikrer høj vedligeholdelsesgrad og klar separation af logik[cite: 1, 3].',
            'code_sample': 'class MembersService:\n    # CRUD-operation med separation af concerns\n    def list_members(self, status=\'active\'):\n        query = \'SELECT * FROM members WHERE status = ?\'\n        return self.db.execute(query, [status])'
        }]