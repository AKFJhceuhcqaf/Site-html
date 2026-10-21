import os
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import html

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key-change-it")

# Подключение к Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    lang = request.args.get('lang', 'ru')
    
    # Получаем актуальные данные профиля из базы данных Supabase
    response = supabase.table("settings").select("*").execute()
    data = response.data[0] if response.data else {
        "name": "Рогожина Екатерина",
        "phone": "+79510354835",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
        "bio_ru": "Перманентный макияж, Brow мастер, Наращивание ресниц",
        "bio_en": "Permanent makeup, Brow master, Eyelash extensions"
    }
    
    return render_template('index.html', data=data, lang=lang)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "admin123":
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', error="Неверный пароль")
            
    if not session.get('logged_in'):
        return render_template('admin.html', needs_login=True)
        
    response = supabase.table("settings").select("*").execute()
    data = response.data[0] if response.data else {}
    return render_template('admin.html', logged_in=True, data=data)

@app.route('/update-settings', methods=['POST'])
def update_settings():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
        
    new_name = html.escape(request.form.get('name', ''))
    new_phone = html.escape(request.form.get('phone', ''))
    new_avatar = html.escape(request.form.get('avatar_url', ''))
    
    supabase.table("settings").update({
        "name": new_name,
        "phone": new_phone,
        "avatar_url": new_avatar
    }).eq("id", 1).execute()
    
    return redirect(url_for('admin'))

@app.route('/book', methods=['POST'])
def book():
    client_name = html.escape(request.form.get('client_name', ''))
    client_phone = html.escape(request.form.get('client_phone', ''))
    service = html.escape(request.form.get('service', ''))
    
    supabase.table("bookings").insert({
        "client_name": client_name,
        "client_phone": client_phone,
        "service": service
    }).execute()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
