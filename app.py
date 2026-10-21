import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Ошибка инициализации Supabase: {e}")

@app.route('/')
def index():
    success = request.args.get('success')
    reviews = []
    
    if supabase:
        try:
            response = supabase.table('reviews').select("*").order('created_at', desc=True).execute()
            reviews = response.data
        except Exception as e:
            print(f"Ошибка при получении отзывов: {e}")
            
    return render_template('index.html', reviews=reviews, success=success)

@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    phone = request.form.get('phone')
    service = request.form.get('service')
    date = request.form.get('date')

    if supabase and name and phone and service and date:
        try:
            supabase.table('bookings').insert({
                "name": name,
                "phone": phone,
                "service": service,
                "date": date
            }).execute()
        except Exception as e:
            print(f"Ошибка при создании записи: {e}")

    return redirect(url_for('index', success=1))

@app.route('/add_review', methods=['POST'])
def add_review():
    author = request.form.get('author')
    text = request.form.get('text')
    date = request.form.get('date')

    if supabase and author and text and date:
        try:
            supabase.table('reviews').insert({
                "author": author,
                "text": text,
                "date": date
            }).execute()
        except Exception as e:
            print(f"Ошибка при добавлении отзыва: {e}")

    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    bookings = []
    if supabase:
        try:
            response = supabase.table('bookings').select("*").order('created_at', desc=True).execute()
            bookings = response.data
        except Exception as e:
            print(f"Ошибка при получении записей для админки: {e}")
            
    return render_template('admin.html', bookings=bookings)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)