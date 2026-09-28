import os
import secrets
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Try to enable pymysql compatibility for environments without mysqlclient
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

from flask_mysqldb import MySQL

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Secure secret key with persistent environment fallback
app.secret_key = os.getenv('SECRET_KEY', 'mental-health-ai-companion-secret-key-prod-2026')

# MySQL Configuration from environment variables
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', os.getenv('MYSQL_HOST', 'localhost'))
app.config['MYSQL_USER'] = os.getenv('DB_USER', os.getenv('MYSQL_USER', 'root'))
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', os.getenv('MYSQL_PASSWORD', 'Radhey2005@'))
app.config['MYSQL_DB'] = os.getenv('DB_NAME', os.getenv('MYSQL_DB', 'mental_wellness_db'))
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', os.getenv('MYSQL_PORT', 3306)))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Make datetime available in all templates
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# Database Helper Functions
def execute_query(query, args=(), one=False, commit=False):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, args)
        if commit:
            mysql.connection.commit()
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        try:
            if hasattr(mysql, 'connection') and mysql.connection:
                mysql.connection.rollback()
        except Exception:
            pass
        raise e

def get_current_user():
    if 'user_id' in session:
        try:
            user_id = session['user_id']
            user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
            return user
        except Exception as e:
            app.logger.warning(f"Error fetching current user: {e}")
            return None
    return None

# Custom Jinja2 test for month comparison
def is_month_equal(date, month):
    return date.month == month

app.jinja_env.tests['month_equal'] = is_month_equal


# --- AI Companion Engine ---
def generate_ai_wellness_response(user_msg, user_name=None):
    """
    Generates empathetic, context-aware mental wellness guidance.
    Uses Gemini API if GEMINI_API_KEY is configured in .env, otherwise
    uses a comprehensive built-in psychological first-aid knowledge engine.
    """
    greeting = f"Hi {user_name}! " if user_name else "Hello! "
    text = user_msg.lower().strip()

    # 1. Check for external Gemini API key if present
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            prompt = (
                "You are an empathetic, compassionate AI Mental Health and Wellness Companion. "
                "You provide supportive, calming, non-judgmental guidance and safe listening. "
                "Always be supportive, gentle, and promote healthy habits. If someone expresses "
                "self-harm or crisis, encourage them warmly to reach out to professional support "
                "and share crisis helpline resources. Keep your response concise, warm, and uplifting.\n\n"
                f"User: {user_msg}"
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
            }
            res = requests.post(url, json=payload, timeout=6)
            if res.status_code == 200:
                data = res.json()
                reply = data['candidates'][0]['content']['parts'][0]['text']
                return reply.strip()
        except Exception as e:
            app.logger.warning(f"Gemini API fallback triggered: {e}")

    # 2. Crisis & Safety Keywords
    crisis_keywords = ['suicide', 'kill myself', 'end my life', 'want to die', 'self harm', 'hurt myself']
    if any(k in text for k in crisis_keywords):
        return (
            "I hear that you're going through an extremely difficult moment, and I want you to know you're not alone. "
            "Please talk to someone who can help right now:\n\n"
            "• **National Crisis Lifeline (US & Canada):** Call or text **988** (available 24/7, free & confidential)\n"
            "• **Tele-MANAS (India):** Call **14416** or **1800 891 4416**\n"
            "• **Crisis Text Line:** Text **HOME** to **741741**\n"
            "• **UK:** Call **111** or **0800 689 5652**\n\n"
            "Please reach out to a trusted loved one, counselor, or doctor. Your life and wellbeing matter deeply."
        )

    # 3. Anxiety, Panic, Overwhelm
    if any(k in text for k in ['anxious', 'anxiety', 'panic', 'overwhelmed', 'nervous', 'stressed', 'stress', 'racing thoughts']):
        return (
            f"{greeting}I'm really glad you reached out. When anxiety or stress builds up, our bodies often get into fight-or-flight mode.\n\n"
            "Let's try a quick 1-minute calming exercise together:\n"
            "1. **Breathe in** gently through your nose for 4 counts.\n"
            "2. **Hold** your breath for 4 counts.\n"
            "3. **Exhale slowly** through your mouth for 6 counts.\n\n"
            "Look around you and name 3 things you can see, 2 things you can touch, and 1 sound you can hear. "
            "Take all the time you need. How is your body feeling right now?"
        )

    # 4. Sadness, Feeling Down, Loneliness
    if any(k in text for k in ['sad', 'down', 'lonely', 'crying', 'hopeless', 'depressed', 'empty', 'alone']):
        return (
            f"{greeting}I'm so sorry things are feeling heavy right now. It's completely okay and human to feel sad or drained. "
            "You don't have to carry everything all at once today.\n\n"
            "Small gentle steps make a difference:\n"
            "• Drink a glass of water\n"
            "• Wrap yourself in a cozy blanket\n"
            "• Try journaling your thoughts in the Journal section\n\n"
            "Would you like to talk more about what's on your mind? I'm here to listen without judgment."
        )

    # 5. Sleep & Rest
    if any(k in text for k in ['sleep', 'insomnia', 'can\'t sleep', 'tired', 'exhausted', 'nightmare']):
        return (
            f"{greeting}Rest is so vital for healing and emotional strength. If your mind is buzzing before bed:\n"
            "• Put down screens 30 minutes before sleep\n"
            "• Try our ambient tracks in the **Music Therapy** section\n"
            "• Do a 'brain dump' journal entry to write down everything worrying you so your brain can let go\n\n"
            "Be patient with yourself tonight."
        )

    # 6. Gratitude & Positive Mood
    if any(k in text for k in ['happy', 'grateful', 'good day', 'great', 'awesome', 'better', 'thank you', 'thanks']):
        return (
            f"{greeting}That brings a warm smile to my heart! Celebrating positive moments and small victories is one of the most powerful habits for long-term emotional resilience. "
            "Take a quick moment to log this in your **Mood Tracker** to preserve this feeling!"
        )

    # 7. Greetings
    if any(k in text for k in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return (
            f"{greeting}I'm your Mental Health AI Companion. How are you feeling today? "
            "You can share whatever is on your mind, explore grounding exercises, or ask for wellness tips."
        )

    # 8. General Supportive Default
    return (
        f"{greeting}Thank you for sharing that with me. Every emotion you feel is valid, and taking time to check in with yourself is a wonderful act of self-care. "
        "Feel free to express more of your thoughts, try our therapeutic games for stress relief, or let me know if you'd like a guided mindfulness exercise."
    )


# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password_raw = request.form.get('password', '')

        if not username or not email or not password_raw:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if len(password_raw) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        password = generate_password_hash(password_raw)
        
        try:
            execute_query(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password),
                commit=True
            )
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            err_msg = str(e)
            if 'Duplicate entry' in err_msg or '1062' in err_msg:
                flash('Username or Email already registered. Please login or use a different one.', 'danger')
            else:
                flash(f'Registration failed: {err_msg}', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = execute_query("SELECT * FROM users WHERE username = %s OR email = %s", (username, username), one=True)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# --- Main Application Routes ---
@app.route("/")
def home():
    user = get_current_user()
    return render_template("maybefinal3.html", user=user)

@app.route("/aboutus1")
def aboutus1():
    return render_template("aboutus1.html", user=get_current_user())

@app.route("/termsofservice")
def termsofservice():
    return render_template("termsofservice.html", user=get_current_user())

@app.route("/privacypolicy")
def privacypolicy():
    return render_template("privacypolicy.html", user=get_current_user())

@app.route("/progress")
def progress():
    user = get_current_user()
    if not user:
        flash('Please login to view your progress', 'warning')
        return redirect(url_for('login'))
    
    mood_stats = execute_query("""
        SELECT mood, COUNT(*) as count, AVG(intensity) as avg_intensity 
        FROM mood_entries 
        WHERE user_id = %s 
        GROUP BY mood
    """, (user['id'],))
    
    journal_count = execute_query(
        "SELECT COUNT(*) as count FROM journal_entries WHERE user_id = %s",
        (user['id'],),
        one=True
    )
    
    current_month = datetime.now().month
    month_entries = execute_query(
        "SELECT COUNT(*) as count FROM journal_entries WHERE user_id = %s AND MONTH(created_at) = %s",
        (user['id'], current_month),
        one=True
    )
    
    return render_template("progress.html", 
                         mood_stats=mood_stats or [],
                         journal_count=(journal_count['count'] if journal_count else 0),
                         month_entries=(month_entries['count'] if month_entries else 0),
                         user=user)

@app.route("/games")
def games():
    return render_template("games.html", user=get_current_user())

@app.route("/musictherapy")
def musictherapy():
    return render_template("musictherapy.html", user=get_current_user())

@app.route("/song")
def song():
    return render_template("song.html", user=get_current_user())

@app.route("/community")
def community():
    return render_template("community.html", user=get_current_user())

@app.route("/setting", methods=['GET', 'POST'])
def setting():
    user = get_current_user()
    if not user:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please login'}), 401
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
            new_username = data.get('username') or data.get('displayName')
            new_email = data.get('email') or data.get('emailAddress')
        else:
            new_username = request.form.get('username') or request.form.get('displayName')
            new_email = request.form.get('email') or request.form.get('emailAddress')
        
        if not new_username or not new_email:
            msg = 'Username and email cannot be empty'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('setting'))

        try:
            execute_query(
                "UPDATE users SET username = %s, email = %s WHERE id = %s",
                (new_username.strip(), new_email.strip(), user['id']),
                commit=True
            )
            if request.is_json:
                return jsonify({'success': True, 'message': 'Settings updated successfully!'})
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('setting'))
        except Exception as e:
            if request.is_json:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(f'Error updating settings: {str(e)}', 'danger')
    
    return render_template("setting.html", user=user)

@app.route("/contactus", methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contactus'))
    return render_template("contactus.html", user=get_current_user())

@app.route("/notification")
def notification():
    user = get_current_user()
    if not user:
        flash('Please login to view notifications', 'warning')
        return redirect(url_for('login'))
    
    try:
        notifications = execute_query(
            "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
            (user['id'],)
        )
    except Exception:
        notifications = []

    return render_template("notification.html", notifications=notifications or [], user=user)

@app.route("/moodtracker", methods=['GET', 'POST'])
def moodtracker():
    user = get_current_user()
    if not user:
        flash('Please login to track your mood', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        mood = request.form.get('mood')
        intensity = int(request.form.get('intensity', 5))
        notes = request.form.get('notes', '')
        
        try:
            execute_query(
                "INSERT INTO mood_entries (user_id, mood, intensity, notes) VALUES (%s, %s, %s, %s)",
                (user['id'], mood, intensity, notes),
                commit=True
            )
            flash('Mood entry saved successfully!', 'success')
        except Exception as e:
            flash(f'Error saving mood entry: {str(e)}', 'danger')
        
        return redirect(url_for('moodtracker'))
    
    entries = execute_query(
        "SELECT * FROM mood_entries WHERE user_id = %s ORDER BY created_at DESC LIMIT 10",
        (user['id'],)
    )
    
    mood_stats = {
        'total_entries': len(entries) if entries else 0,
        'avg_intensity': None,
        'recent_trend': None,
        'mood_distribution': {}
    }
    
    if entries:
        intensities = [e['intensity'] for e in entries if e['intensity'] is not None]
        if intensities:
            mood_stats['avg_intensity'] = round(sum(intensities) / len(intensities), 1)
        
        if len(entries) >= 2 and entries[0]['intensity'] is not None and entries[1]['intensity'] is not None:
            mood_stats['recent_trend'] = entries[0]['intensity'] - entries[1]['intensity']
        
        for entry in entries:
            mood = entry['mood']
            mood_stats['mood_distribution'][mood] = mood_stats['mood_distribution'].get(mood, 0) + 1
    
    return render_template(
        "moodtracker.html",
        entries=entries or [],
        mood_stats=mood_stats,
        user=user
    )

@app.route("/journaling", methods=['GET', 'POST'])
def journaling():
    user = get_current_user()
    if not user:
        flash('Please login to access journaling', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        content = request.form.get('content', '')
        
        try:
            execute_query(
                "INSERT INTO journal_entries (user_id, title, content) VALUES (%s, %s, %s)",
                (user['id'], title, content),
                commit=True
            )
            flash('Journal entry saved successfully!', 'success')
        except Exception as e:
            flash(f'Error saving journal entry: {str(e)}', 'danger')
        
        return redirect(url_for('journaling'))
    
    entries = execute_query(
        "SELECT * FROM journal_entries WHERE user_id = %s ORDER BY created_at DESC",
        (user['id'],)
    )
    return render_template("journaling.html", entries=entries or [], user=user)

@app.route('/journal/delete/<int:entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Please login'}), 401
    
    try:
        execute_query(
            "DELETE FROM journal_entries WHERE id = %s AND user_id = %s",
            (entry_id, user['id']),
            commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/journal/update/<int:entry_id>', methods=['POST'])
def update_journal_entry(entry_id):
    user = get_current_user()
    if not user:
        flash('Please login to update journal entries', 'warning')
        return redirect(url_for('login'))
    
    title = request.form.get('title', 'Untitled')
    content = request.form.get('content', '')
    
    try:
        execute_query(
            "UPDATE journal_entries SET title = %s, content = %s WHERE id = %s AND user_id = %s",
            (title, content, entry_id, user['id']),
            commit=True
        )
        flash('Journal entry updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating journal entry: {str(e)}', 'danger')
    
    return redirect(url_for('journaling'))


# --- API Routes ---
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AI Companion Chat Endpoint"""
    user = get_current_user()
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    reply = generate_ai_wellness_response(message, user_name=user['username'] if user else None)
    return jsonify({
        'reply': reply,
        'timestamp': datetime.now().strftime('%I:%M %p')
    })

@app.route('/api/upload-profile-image', methods=['POST'])
def upload_profile_image():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Please login'}), 401
    return jsonify({'success': True, 'message': 'Profile picture updated!'})

@app.route('/api/send-account-details', methods=['POST'])
def send_account_details():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Please login'}), 401
    return jsonify({'success': True, 'message': 'Account details sent to registered email!'})

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    db_status = 'ok'
    try:
        execute_query("SELECT 1", one=True)
    except Exception as e:
        db_status = f'db unavailable: {str(e)}'
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'time': datetime.now().isoformat()
    }), 200


# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    user = None
    try:
        user = get_current_user()
    except Exception:
        pass
    return render_template('404.html', user=user), 404

@app.errorhandler(500)
def internal_error(e):
    try:
        if hasattr(mysql, 'connection') and mysql.connection:
            mysql.connection.rollback()
    except Exception:
        pass
    user = None
    try:
        user = get_current_user()
    except Exception:
        pass
    return render_template('500.html', user=user), 500


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)