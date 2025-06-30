from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import User
import pymysql

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return pymysql.connect(
        host='db',
        user='paperless',
        password='paperless',
        database='paperless',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, is_superuser, department_id, role FROM auth_user WHERE username = %s AND password = %s",
                    (username, password)
                )
                user_data = cursor.fetchone()
                if user_data:
                    session['username'] = user_data['username']
                    session['is_superuser'] = user_data['is_superuser']
                    session['department_id'] = user_data['department_id']
                    session['role'] = user_data['role']
                    return redirect(url_for('documents.admin'))
        finally:
            conn.close()
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))