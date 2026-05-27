import os
import sys
sys.path.insert(0, '/opt/taskboard/bot')

from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from main import app
from database import Aufgabe, session

# Einfacher User für Login
class User(UserMixin):
    id = 1

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = os.getenv('DASHBOARD_USER')
        password = os.getenv('DASHBOARD_PASS')
        if request.form['username'] == user and request.form['password'] == password:
            login_user(User())
            return redirect(url_for('dashboard'))
        flash('Falscher Benutzername oder Passwort!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    filter_status = request.args.get('filter', 'offen')
    if filter_status == 'alle':
        aufgaben = session.query(Aufgabe).order_by(Aufgabe.erstellt_am.desc()).all()
    elif filter_status == 'erledigt':
        aufgaben = session.query(Aufgabe).filter_by(erledigt=True).order_by(Aufgabe.erstellt_am.desc()).all()
    else:
        aufgaben = session.query(Aufgabe).filter_by(erledigt=False).order_by(Aufgabe.erstellt_am.desc()).all()
    return render_template('dashboard.html', aufgaben=aufgaben, filter_status=filter_status)

@app.route('/erledigt/<int:aufgabe_id>')
@login_required
def mark_erledigt(aufgabe_id):
    aufgabe = session.get(Aufgabe, aufgabe_id)
    if aufgabe:
        aufgabe.erledigt = True
        session.commit()
    return redirect(url_for('dashboard'))

@app.route('/loeschen/<int:aufgabe_id>')
@login_required
def loeschen(aufgabe_id):
    aufgabe = session.get(Aufgabe, aufgabe_id)
    if aufgabe:
        session.delete(aufgabe)
        session.commit()
    return redirect(url_for('dashboard'))

from main import login_manager
from flask_login import current_user

@login_manager.user_loader
def load_user(user_id):
    return User()
