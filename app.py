import os
import html
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secure-random-key-change-it-12345")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception:
    supabase = None

@app.route('/')
def index():
    lang = request.args.get('lang', 'ru')
    data = {
        "name": "Рогожина Екатерина",
        "phone": "+79510354835",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
        "bio_ru": "Перманентный макияж, Brow мастер, Наращивание ресниц",
        "bio_en": "Permanent makeup, Brow master, Eyelash extensions"
    }
    if supabase:
        try:
            response = supabase.table("settings").select("*").execute()
            if response.data:
                data.update(response.data[0])
        except Exception:
            pass
    return render_template('index.html', data=data, lang=lang)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        entered_password = request.form.get('password', '')
        
        # Получаем данные настроек из базы (включая хэш пароля)
        db_data = {}
        if supabase:
            try:
                res = supabase.table("settings").select("*").execute()
                if res.data:
                    db_data = res.data[0]
            except Exception:
                pass
        
        # Дефолтный хэш (если в базе еще нет своего, по умолчанию "admin123")
        stored_hash = db_data.get('admin_password_hash') or generate_password_hash("admin123")
        
        if check_password_hash(stored_hash, entered_password):
            session['is_authenticated'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', needs_login=True, error="Неверный пароль")
            
    if not session.get('is_authenticated'):
        return render_template('admin.html', needs_login=True)
        
    data = {}
    if supabase:
        try:
            response = supabase.table("settings").select("*").execute()
            if response.data:
                data = response.data[0]
        except Exception:
            pass
            
    return render_template('admin.html', logged_in=True, data=data)

@app.route('/update-settings', methods=['POST'])
def update_settings():
    if not session.get('is_authenticated'):
        return redirect(url_for('admin'))
        
    new_name = html.escape(request.form.get('name', ''))
    new_phone = html.escape(request.form.get('phone', ''))
    new_avatar = html.escape(request.form.get('avatar_url', ''))
    
    if supabase:
        try:
            supabase.table("settings").update({
                "name": new_name,
                "phone": new_phone,
                "avatar_url": new_avatar
            }).eq("id", 1).execute()
        except Exception:
            pass
    
    return redirect(url_for('admin'))

@app.route('/change-password', methods=['POST'])
def change_password():
    if not session.get('is_authenticated'):
        return redirect(url_for('admin'))
        
    new_pass = request.form.get('new_password', '')
    if len(new_pass) >= 6:
        new_hash = generate_password_hash(new_pass)
        if supabase:
            try:
                supabase.table("settings").update({
                    "admin_password_hash": new_hash
                }).eq("id", 1).execute()
            except Exception:
                pass
                
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('is_authenticated', None)
    return redirect(url_for('index'))

@app.route('/book', methods=['POST'])
def book():
    client_name = html.escape(request.form.get('client_name', ''))
    client_phone = html.escape(request.form.get('client_phone', ''))
    service = html.escape(request.form.get('service', ''))
    if supabase:
        try:
            supabase.table("bookings").insert({
                "client_name": client_name,
                "client_phone": client_phone,
                "service": service
            }).execute()
        except Exception:
            pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
