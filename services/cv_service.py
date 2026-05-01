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
            db.execute('CREATE TABLE IF NOT EXISTS cv_references (id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT, person TEXT, title TEXT, quote TEXT)')
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
            ('intro', 'Jeg er en erfaren digital brobygger og teknisk konsulent med knap 20 års erfaring i at skabe sammenhæng mellem komplekse data, IT-systemer og de mennesker, der skal bruge dem. Min kernekompetence er procesoptimering; jeg fjerner friktion i organisationer ved at skabe smarte systemer og automatiseringer, der gør hverdagen nemmere for mine kolleger og kunder.'),
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
            ('Softwareudvikling & Data', 'Stærke kompetencer i Python (videregående niveau) og SQL. Jeg anvender objektorienteret programmering og databasemodellering til at håndtere store tekniske datasæt.'),
            ('Specialist CAD & BIM', 'Ekspert i Tekla Structures, AutoCAD (20 år) og Revit Architecture. Unik evne til at skabe integration mellem 3D-modeller og produktionsdata.'),
            ('Systemoptimering', 'Teknisk specialist i implementering af systemer som HSBMake. Erfaring med at overtage og fuldføre komplekse udrulninger fra eksterne konsulenter.'),
            ('Automation', 'Udvikling af automatiserede funktioner og scripts til procesoptimering. Fjerner manuelle arbejdsgange gennem intelligent kode.'),
            ('IT-Infrastruktur & ERP', 'Erfaring med drift og fejlfinding i komplekse miljøer, herunder SAP, samt fuld hardware- og software-opsætning.'),
            ('Teknisk Rådgivning', 'Seniorerfaring som "Trusted Advisor" i hele Norden. Ekspert i teknisk it-support, undervisning og onboarding.')
        ]
        db.executemany('INSERT INTO cv_skills (category, description) VALUES (?, ?)', skills)

        # --- ERHVERVSERFARING (VERIFICERET MOD ALLE KILDER) ---
        exp = [
            ('Design Data Specialist', 'Scandi Byg, Løgstør', 'Aug 2024 – Apr 2025', 
             'Ansvarlig for teknisk og menneskelig implementering af HSBcad/HSBMake til Revit og AutoCAD. '
             'Fungerede som bindeled mellem tegnestue og produktion. Kvalitetssikrede softwarens reelle formåen og udarbejdede udrulningsplan.'),
            
            ('BIM Udvikler / Tegner', 'Søgaard Stålbyg, Skive (Remote)', 'Aug 2023 – Jul 2024', 
             'Headhuntet direkte fra konsulentrolle. Udviklede og automatiserede Tekla-opsætninger. '
             'Omkonstruerede "kronen" på projektet "Posten" i København for at sikre fejlfri bygbarhed direkte i softwaren.'),
            
            ('Software tekniker & konsulent', 'BuildingPoint Scandinavia (Remote)', 'Okt 2021 – Jul 2023', 
             'Teknisk rådgiver og supportspecialist for Tekla Structures i Norden. '
             'Trænede brugere fra basis- til avanceret niveau og blev udlejet som specialist til komplekse kundeprojekter.'),
            
            ('Produktionstegner', 'Ambercon, Støvring', 'Dec 2020 – Sep 2021', 
             '3D tegner og intern supporter i et komplekst produktionsmiljø. '
             'Fungerede som teknisk support for nye brugeres overgang fra AutoCAD 3D til Tekla Structures i forbindelse med projektering af "Papirøen".'),
            
            ('BIM Udvikler', 'Spæncom, Aalborg', 'Feb 2017 – Nov 2020', 
             'Udviklede funktioner og kodede statiske beregninger direkte i softwaren for at reducere tegnetid. '
             'International underviser for tegnestuer i Danmark, Polen, Rumænien og Estland.'),
            
            ('Teknisk Designer', 'NIRAS, Aalborg', 'Jan 2012 – Jan 2017', 
             'Håndterede ledningsregistrering (DANDAS), 3D modellering og GPS-opmåling i marken. '
             'Ansvarlig for oplæring af internationale udvekslingsstuderende og praktikanter.'),
            
            ('Teknisk Designer (Udvikling)', 'PN Beslagfabrik, Brønderslev', 'Sep 2009 – Aug 2011', 
             'Modellerede og standardiserede dokumentation for hele sortimentet i CoCreate uden forudgående træning. '
             'Tæt dialog med produktionen for at sikre gnidningsfri fremstilling.'),
            
            ('Teknisk Designer', 'DS Stålkonstruktion, Hobro', 'Jul 2008 – Feb 2009', 
             'Udarbejdelse af præcise produktions- og arbejdstegninger af stålspær til store stålhaller i AutoCAD 2D.'),
            
            ('Produktionsmedarbejder', 'PUMAC, Svenstrup', 'Sep 2007 – Jun 2008', 
             'Betjente CNC-maskiner, laserskærere og revolverstansere på aftenhold. '
             'Opbyggede den praktiske forståelse for produktionsmiljøet, som i dag danner grundlaget for mit IT-arbejde.'),
            
            ('Teknisk Designer & Maskinoperatør', 'Nytech, Vester Hassing', 'Jan 2007 – Aug 2007', 
             'Bindeled mellem design og udførelse. Udarbejdede 3D-grundlag i SolidWorks og '
             'programmerede/betjente selvstændigt laserskærere og revolverstansere.'),
            
            ('Teknisk Designer Elev', 'Martin Professional, Frederikshavn', 'Sep 2004 – Jun 2006', 
             'Udlært inden for maskin- og produktionstegning i den Produktionstekniske Afdeling (PTA). '
             'Udarbejdede styklister og løste samleudfordringer i tæt samarbejde med ingeniører.')
        ]
        db.executemany('INSERT INTO cv_experience (title, company, period, description) VALUES (?, ?, ?, ?)', exp)

        # --- UDDANNELSE & KURSER ---
        edu = [
            ('Teknisk designer (EUD)', 'Aalborg tekniske Skole', '2003 - 2006', 
             'Omfatter IT, beregning, materialelære, 3D-animation og teknisk dokumentation.'),
            ('Videregående Python Programmering (Karakter: 12)', 'Itucation', '2025', 
             'Intensivt kursus med fokus på Flask, SQLite og Full-stack udvikling. Udviklede webbaseret medlemsdatabase.'),
            ('HSB Make & HSB on Revit', 'HSBcad UK', '2025', 
             'Specialiseret træning i databasehåndtering og implementering direkte hos softwareudviklerne.'),
            ('Power BI for begyndere', 'STI / Selvstudie', '2025', 
             'Fokus på datavisualisering og evnen til at omsætte rå data til forretningsværdi.'),
            ('Tillidsrepræsentantuddannelsen', 'Teknisk Landsforbund', '2018', 
             'Fokus på forhandlingsteknik, arbejdsret, trivsel og konfliktløsning.'),
            ('Effektiv kommunikation', 'Teknologisk Institut', '2018', 
             'Værktøjer til konflikthåndtering, forandringsledelse og tværfaglig kommunikation.')
        ]
        db.executemany('INSERT INTO cv_education (title, institution, period, description) VALUES (?, ?, ?, ?)', edu)

        # --- FRIVILLIGT & TILLIDSHVERV ---
        vol = [
            ('Bestyrelsesmedlem & Frivillig', 'Troopers for Charity', '2022 – Nu', 
             'Besøg hos syge børn som karakteren Darth Maul. Skaber magiske frirum i svære situationer.'),
            ('Lokalt Uddannelsesudvalg', 'Teknisk Design, Aalborg', '2024 – 2026', 
             'Udpeget medlem med fokus på at sikre kvaliteten og fremtiden for erhvervsuddannelsen.'),
            ('Bestyrelsesmedlem', 'TL Nordjylland', '2022 – 2026', 
             'Organisatorisk arbejde og medlemsinteresser frem til planlagt afgang marts 2026.'),
            ('Tillidsrepræsentant', 'Spæncom', '2018 – 2020', 
             'Fokus på trivsel, kommunikation og samarbejde på tværs af faggrupper.')
        ]
        db.executemany('INSERT INTO cv_volunteer (title, company, period, description) VALUES (?, ?, ?, ?)', vol)

        # --- REFERENCER ---
        refs = [
            ('Scandi Byg', 'Mads Seneca Simonsen', 'Adm. Direktør', "Det er mig en fornøjelse at anbefale Kasper Groth Jensen, som i sin tid hos Scandi Byg har vist sig som en yderst kompetent og engageret medarbejder. Kasper har i sin rolle som Design Data Specialist spillet en central rolle i projektledelsen for digitalisering af produktionstegninger samt implementering af nye værktøjer. Blandt hans vigtigste bidrag kan nævnes: Projektledelse og implementering af nye IT-værktøjer såsom HSB Make, til effektivisering af virksomhedens arbejdsprocesser. Tværfagligt samarbejde mellem forskellige afdelinger, hvor han har fungeret som bindeled mellem teknisk design, IT og produktion. Stærk teknisk indsigt i Revit, AutoCAD og BIM-systemer, som han har anvendt til at kvalitetssikre løsninger og sikre at disse understøttede Scandi Byg's behov. Kasper har en analytiske tilgang, strukturerede i sine arbejdsmetoder og evne til at formidle tekniske løsninger på en letforståelig måde. Han er en teamplayer med en stærk problemløsningsevne og et proaktivt mindset, hvilket har gjort ham til en værdsat medarbejder og sparringspartner for både kollegaer og ledelse. Jeg kan derfor give Kasper mine varmeste anbefalinger og er overbevist om, at han vil være en stærk ressource i virksomheder, som har behov for Kaspers kompetencer."),
            ('Scandi Byg', 'Daria Rzhavtseva', 'Projekteringsleder', 'Jeg alligevel gerne dele min oplevelse af dig som en positiv, professionel og troværdig kollega. Selvom vi ikke har arbejdet tæt sammen, har vores dialoger altid været præget af klarhed og konstruktivitet. Du fremstår som en ansvarlig og engageret person - nem at samarbejde med og altid klar til at hjælpe. Jeg husker tydeligt, hvordan du rakte hånden ud med det samme, da jeg havde brug for det. Det siger meget om dig - både fagligt og menneskeligt. De bedste anbefalinger herfra!'),
            ('Scandi Byg', 'Katya Aaen', 'IKT og BIM Specialist', 'Du er simpelthen en god kollega, fornøjelse at arbejde med og nemt at snakke med. Igennem vores samarbejde fik jeg oplevet dig som vel organiseret og altid konstruktiv person.'),
            ('BuildingPoint Scandinavia / EDRMedeso', 'Marcus Rodriguez', 'Sales and Operations Manager', 'This is to certify that Kasper Groth Jensen has been employed by EDRMedeso AS. Position: Technical Consultant. Periode: between 01/10/2021 - 21.07.2023. The employment type: Full time. Work tasks: Technical Consultantcy, Training in Software, Development of technical systems around our software, user support, demonstration of solutions. During the employment Kasper Groth Jensen has demonstrated excellent working skills and behaviour.'),
            ('BuildingPoint Scandinavia / EDRMedeso', 'Måns Alhem', 'Senior Technical Specialist', 'Kasper och jag jobbade ihop på BuildingPoint Scandinavia. Kasper gjorde ett mycket bra jobb hos oss och det var tråkigt att han slutade. Väldigt uppskattad på kundsupport och alltid ett glatt humör!'),
            ('Spæncom A/S (Consolis)', 'Kim Schmeltz', 'BIM Chef / manager', "Kasper Groth Jensen har været ansat på fuldtid som BIM (Bygnings Information Modellering) udvikler hos Spæncom A/S i perioden 1. februar 2017 til 30. november 2020. Kasper Groth Jensen fratræder sin stilling efter eget ønske. Arbejdsområdet og opgaverne for Kasper, har været vekslende og meget bred, men det primær fokusområde for Kasper har været at medvirket til at udvikle Spæncom's design værktøjer til programmet Tekla Structures samt medvirkende til at flytte virksomheden i en mere digital retning ved brug af dette program. I rollen som BIM udvikler har Kasper været involveret i udvikling på tværs af vores organisation som involvere parter fra både Norge, Sverige, Finland, Estland, Polen og flere til. Kasper har med denne involvering gjort brug af hans kommunikative evner til at formidle og dokumentere strategiske budskaber på engelsk for at fremme den fælles udvikling i virksomheden. Kasper har varetaget sit arbejde som BIM udvikler med stor engagement og interesse. Kasper har været god til både at arbejde selvstændig og sammen med andre når det drejer sig om udvikling af design værktøjer til andre kollegaer. Kasper har desuden bidraget til øget social kapital i virksomhed bl.a. gennem hans måde at yde god support og støtte til kollegaerne. Kaspers gode evner til at sætte sig hurtigt ind i nye opgaver og se løsninger frem for udfordringer, har jeg sat stor pris på i den tid jeg har haft fornøjelsen af at have Kasper ansat i mit team. Jeg anser Kasper som at være en af de mere loyale medarbejder jeg har haft i mit team, og det er mig derfor en fornøjelse at anbefale Kasper til lignende udviklingsrolle."),
            ('Spæncom A/S (Consolis)', 'Morten Kaasik', 'Product Manager - Design tools and Buisness Intelligence', 'I worked together with Kasper on cross-team collaborative projects in the Consolis group. Kasper was always helpful in assisting the Consolis central development projects and went above-and-beyond in helping align the visions of Spaencom to that of Consolis central development team. I had very good experience in working with Kasper.'),
            ('Spæncom A/S (Consolis)', 'Berit Amdi', 'Konstruktør og outsourcings koordinator', 'Vi arbejdede sammen hos Spæcom. Du var altid i godt humør og var altid yderst hjælpsom. Og meget grundig når du skulle hjælpe med noget, du slap ikke opgaven før du var sikker på at din hjælp var landet godt, altid meget tålmodig.'),
            ('Niras', 'Dorte Juul Sørensen', 'Projektleder', 'Jeg havde fornøjelsen at samarbejde med dig i en årrække i Niras. Jeg oplevede dig som en meget omhyggelig og omgængelig medarbejder, som satte en ære i at levere et godt produkt.'),
            ('Niras', 'Karen Vinther Toft', 'Teknisk Assistent, GIS & opmåling', 'Jeg er kommet til at kende Kasper, som en dygtig, behagelig og imødekommende person, som altid er behjælpelig på bedste måde, når jeg har brug for sparring omkring opgaverne. Kasper er godt inde i programmer og data og er beredvillig med få løst eventuelle problemstillinger, som jeg har, på bedste måde. Det is med fuld opbakning, at Brønderslev Forsyning giver Kasper de bedste anbefalinger og ønsker ham held og lykke fremover. Med venlig hilsen Karen Vinther Toft Brønderslev Forsyning A/S')
        ]
        db.executemany('INSERT INTO cv_references (company, person, title, quote) VALUES (?, ?, ?, ?)', refs)
        db.commit()

    def get_all_cv_data(self):
        conn = self.get_db()
        try:
            profile_rows = conn.execute('SELECT key, value FROM cv_profile').fetchall()
            ref_rows = conn.execute('SELECT company, person, title, quote FROM cv_references').fetchall()
            
            # Gruppér referencer efter firma
            references_by_company = {}
            for r in ref_rows:
                comp = r['company']
                if comp not in references_by_company:
                    references_by_company[comp] = []
                references_by_company[comp].append(dict(r))

            data = {
                'profile': {row['key']: row['value'] for row in profile_rows},
                'about': conn.execute('SELECT point FROM cv_about').fetchall(),
                'languages': conn.execute('SELECT language, level FROM cv_languages').fetchall(),
                'metadata': {row['label']: row['value'] for row in conn.execute('SELECT label, value FROM cv_metadata').fetchall()},
                'skills': conn.execute('SELECT category, description FROM cv_skills').fetchall(),
                'keywords': conn.execute('SELECT keyword FROM cv_keywords').fetchall(),
                'experience': conn.execute('SELECT title, company, period, description FROM cv_experience').fetchall(),
                'education': conn.execute('SELECT title, institution, period, description FROM cv_education').fetchall(),
                'volunteer': conn.execute('SELECT title, company, period, description FROM cv_volunteer').fetchall(),
                'references_by_company': references_by_company
            }
            return data
        finally:
            conn.close()

    def get_showcase(self):
        return [{
            'title': 'Eksamensprojekt: Medlemssystem (Troopers for Charity)',
            'grade': '12',
            'tech': 'Python, Flask, SQLite, Pandas, Matplotlib',
            'description': (
                'Dette system er udviklet som et professionelt administrationsværktøj til medlemsstyring. '
                'Applikationen demonstrerer avanceret brug af Python til procesoptimering og sikker datahåndtering.\n\n'
                'Tekniske highlights:\n'
                '- Three-Tier Architecture for maksimal vedligeholdelsesgrad.\n'
                '- Sikker håndtering af følsomme data (CPR) via krypteringslag.\n'
                '- Dynamisk analytics-modul med automatiseret generering af statistiske grafer.'
            ),
            'code_sample': '# Eksempel på Servicelagets logik\nclass MembersService:\n    def list_members(self, status=\'active\'):\n        return self._db.list_members(status)'
        }]