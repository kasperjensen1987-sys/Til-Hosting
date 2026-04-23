from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, make_response
from datetime import date, datetime
import os
from functools import wraps

from services.members_service import (
    MembersService,
    cpr_display,
    cpr_display_compact, # kompakt CPR ddmmyy-xxxx
    age_from_full_cpr,
)
from services.auth_service import AuthService
from services.analytics_service import AnalyticsService

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)
    return wrapper

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY', 'dev-change-me')
    app.config['DATABASE'] = os.path.join(app.root_path, 'storage', 'tfc_members.db')
    os.makedirs(os.path.join(app.root_path, 'storage'), exist_ok=True)

    # hjælpere til Jinja (bruges i templates)
    app.jinja_env.globals['cpr_display'] = cpr_display
    app.jinja_env.globals['cpr_display_compact'] = cpr_display_compact
    app.jinja_env.globals['age_from_full_cpr'] = age_from_full_cpr
    return app

app = create_app()
members_service = MembersService(app.config['DATABASE'])
auth_service = AuthService(app.config['DATABASE'])
analytics_service = AnalyticsService(app.config['DATABASE'])

# --- NY ROUTE: FORSIDE / INTERAKTIVT CV ---
@app.route('/')
def index():
    profile = {
        'name': 'Kasper Groth Jensen',
        'title': 'Digital Specialist & Procesoptimering',
        'tagline': 'Strategisk brobygger mellem IT, bygbarhed og mennesker',
        'intro': 'Med et 12-tal i Videregående Programmering og 20 års erfaring som teknisk bindeled, specialiserer jeg mig i at transformere komplekse forretningsbehov til automatiserede løsninger.',
        'talents': ['Udviklende', 'Målrettet', 'Problemløser', 'Disciplineret', 'Positiv'],
        'disc': 'Kompetence & Stabilitet (C/S profil)',
        'linkedin': 'https://www.linkedin.com/in/kaspergrothjensen',
        'thingiverse': 'https://www.thingiverse.com/KgrothJensen/designs'
    }
    
    showcase = [
        {
            'title': 'Eksamensprojekt: Medlemssystem',
            'grade': '12',
            'tech': 'Python, Flask, SQLite, Pandas',
            'description': 'Systemet er udviklet med Three-Tier Architecture (Service-, Database- og Model-lag), hvilket sikrer høj vedligeholdelsesgrad og klar separation af logik.',
            'code_sample': 'class MembersService:\n    # CRUD-operation med separation af concerns\n    def list_members(self, status=\'active\'):\n        query = \'SELECT * FROM members WHERE status = ?\'\n        return self.db.execute(query, [status])'
        }
    ]
    
    return render_template('cv.html', profile=profile, showcase=showcase)

# --- DINE EKSISTERENDE ROUTES TIL MEDLEMSSYSTEMET ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        row = auth_service.verify(username, password)
        if row:
            session['user_id'] = row['id']
            session['username'] = row['username']
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Forkert brugernavn eller adgangskode', 'error')
    return render_template('Index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_active = members_service.count_by_status('active')
    total_inactive = members_service.count_by_status('inactive')
    # URLs til grafer med cache-bust i template
    chart_urls = {
        'membership': url_for('analytics_chart', chart='membership'),
        'age_buckets': url_for('analytics_chart', chart='age_buckets'),
        'age_gender': url_for('analytics_chart', chart='age_gender'),
        'child_vs_adult': url_for('analytics_chart', chart='child_vs_adult'),
    }
    return render_template(
        'dashboard.html',
        total_active=total_active,
        total_inactive=total_inactive,
        chart_urls=chart_urls
    )

@app.route('/members')
@login_required
def members_list():
    status = request.args.get('status', 'active')
    rows = members_service.list_members(status)
    return render_template(
        'members_list.html',
        members=rows,
        status=status,
    )

@app.route('/members/<int:member_id>')
@login_required
def members_view(member_id):
    m = members_service.get_member(member_id)
    if not m:
        return 'Ikke fundet', 404
    return render_template('member_detail.html', member=m)

@app.route('/members/new', methods=['GET', 'POST'])
@login_required
def members_new():
    if request.method == 'POST':
        ok, msg = members_service.create_member(request.form)
        if ok:
            flash(msg, 'success')
            return redirect(url_for('members_list'))
        else:
            flash(msg, 'error')
    return render_template('members_form.html')

@app.route('/members/<int:member_id>/edit', methods=['GET', 'POST'])
@login_required
def members_edit(member_id):
    if request.method == 'POST':
        ok, msg = members_service.update_member(member_id, request.form)
        if ok:
            flash(msg, 'success')
            return redirect(url_for('members_list'))
        else:
            flash(msg, 'error')
    row = members_service.get_member(member_id)
    if not row:
        return 'Ikke fundet', 404
    return render_template('members_edit.html', member=row)

@app.route('/members/<int:member_id>/toggle')
@login_required
def members_toggle(member_id):
    rows = members_service.list_members(None)
    m = next((r for r in rows if r['id'] == member_id), None)
    if not m:
        return 'Ikke fundet', 404
    if m['status'] == 'inactive':
        members_service.reactivate(member_id)
        flash('Medlem genaktiveret', 'success')
        return redirect(url_for('members_list', status='active'))
    return redirect(url_for('members_terminate', member_id=member_id))

@app.route('/filter/age')
@login_required
def filter_age():
    group = request.args.get('group')
    min_age = request.args.get('min', type=int)
    max_age = request.args.get('max', type=int)
    rows = members_service.filter_age(group=group, min_age=min_age, max_age=max_age)
    status = 'under18' if group == 'under18' else 'filtered'
    return render_template(
        'members_list.html',
        members=rows,
        status=status,
    )

@app.route('/renewals-overview')
@login_required
def renewals_overview():
    base_year = request.args.get('base_year', type=int) or date.today().year
    renewals_this = members_service.renewals_in_year(base_year)
    renewals_next = members_service.renewals_in_year(base_year + 1)
    return render_template(
        'renewals.html',
        base_year=base_year,
        renewals_this=renewals_this,
        renewals_next=renewals_next
    )

@app.route('/renewals/print')
@login_required
def renewals_print():
    year = request.args.get('year', type=int)
    if not year:
        return 'Manglende år', 400
    rows = members_service.renewals_in_year(year)
    return render_template(
        'renewals_print.html',
        year=year,
        rows=rows,
        printed_at=datetime.now().strftime('%d-%m-%Y %H:%M')
    )

@app.route('/members/<int:member_id>/terminate', methods=['GET', 'POST'])
@login_required
def members_terminate(member_id):
    if request.method == 'POST':
        leave_date = request.form.get('leave_date', '').strip()
        leave_reason = request.form.get('leave_reason', '').strip()
        if not leave_date or not leave_reason:
            flash('Angiv både udmeldelsesdato og årsag.', 'error')
            return redirect(url_for('members_terminate', member_id=member_id))
        try:
            datetime.strptime(leave_date, '%d-%m-%Y')
        except ValueError:
            flash('Ugyldig dato. Brug formatet DD-MM-YYYY.', 'error')
            return redirect(url_for('members_terminate', member_id=member_id))
        members_service.set_inactive(member_id, leave_date, leave_reason)
        flash('Medlem udmeldt', 'success')
        return redirect(url_for('members_list', status='inactive'))

    rows = members_service.list_members(None)
    m = next((r for r in rows if r['id'] == member_id), None)
    if not m:
        return 'Ikke fundet', 404
    today = date.today().strftime('%d-%m-%Y')
    return render_template('members_terminate.html', member=m, today=today)

# besked om permanent sletning
@app.route('/members/<int:member_id>/delete', methods=['POST'])
@login_required
def members_delete(member_id: int):
    ok = members_service.delete_member(member_id)
    if ok:
        flash('Medlem slettet permanent.', 'success')
    else:
        flash('Medlem ikke fundet.', 'error')
    return redirect(url_for('members_list', status='inactive'))

# Endpoints til grafer
@app.route('/analytics/<chart>.png')
@login_required
def analytics_chart(chart: str):
    """
    Server PNG-graf ingen caching så den altid følger databasen
    """
    buf = analytics_service.render(chart)
    resp = make_response(send_file(buf, mimetype='image/png'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

if __name__ == '__main__':
    # Render bruger port 5000 som standard, men host skal være 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)