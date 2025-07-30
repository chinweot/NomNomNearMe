from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db import init_auth_db, register_user, login_user, save_event, get_saved_events, delete_saved_event
from forms import RegistrationForm, LoginForm
from apis.event_handler import search_all_events
from apis.user_events import init_user_events_db, add_user_event, get_user_events
from apis.google_events import get_google_events
from datetime import datetime, timedelta, timezone
from mailer import send_email
from phone_api import send_sms
import sqlite3
import google.generativeai as genai
import db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Wnv1I6Tsd7'

# Configure Gemini API
import os
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None

def gemini_tag(title, description):
    if not gemini_model:
        # fallback
        return 'other'
    prompt = f"""Given the following event title and description, return a single tag (one word, lowercase) that best categorizes the event. Example tags: food, music, sports, comedy, networking, art, education, festival, other. If unsure, return 'other'.\n\nTitle: {title}\nDescription: {description}\nTag:"""
    try:
        response = gemini_model.generate_content(prompt)
        tag = response.text.strip().split()[0].lower()
        # Only allow known tags
        allowed_tags = {'food','music','sports','comedy','networking','art','education','festival','other'}
        return tag if tag in allowed_tags else 'other'
    except Exception as e:
        print(f"Gemini tag error: {e}")
        return 'other'


init_auth_db()
init_user_events_db()
#MOCK_USER_ID = 1
# ---------- AUTHENTICATION ----------

# ---------- USER FREE EVENTS ----------

@app.route("/post_event", methods=["GET", "POST"])
def post_event():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        event_time = request.form.get("event_time", "").strip()
        timezone = request.form.get("timezone", "").strip()
        if not (title and location and event_time and timezone):
            return render_template("post_event.html", error="All fields are required.")
        add_user_event(title, location, event_time, timezone)
        return redirect(url_for("user_events"))
    return render_template("post_event.html")

@app.route("/user_events")
def user_events():
    events = get_user_events()
    return render_template("user_events.html", events=events)

# ---------- AUTHENTICATION ----------

# --- SIGN IN PAGE 

@app.route("/signup", methods=['GET', 'POST'])
def signup():

    # error handling, easier to test w 
    try:
        form = RegistrationForm()
        print("Form created successfully")
    except Exception as e:
        print(f"Error creating form: {e}")
        return f"Form creation error: {e}"

    error_message = None  # Ensure this is always defined

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data 
        password = form.password.data 
        phone = form.phone.data

        result = register_user(username, email, password, phone)
        if result['status'] == 'success':
            session['user_id'] = result['user_id']
            return redirect(url_for('onboarding_location'))
        else: 
            print(f"REGISTRATION FAILED WITH STATUS {result['status']}")
            error_message = result['message']  # Capture the error message

    return render_template("signup.html", form=form, error_message=error_message)

# ---------- ONBOARDING FLOW ----------

@app.route("/onboarding/location", methods=['GET', 'POST'])
def onboarding_location():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        if location:
            session['user_location'] = location
            return redirect(url_for('onboarding_interests'))
    
    return render_template("onboarding_location.html")

@app.route("/onboarding/interests", methods=['GET', 'POST'])
def onboarding_interests():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        interests = request.form.get('interests', '').strip()
        if interests:
            session['user_interests'] = interests
            return redirect(url_for('for_you'))
    
    return render_template("onboarding_interests.html")

# --- LOGIN PAGE 

@app.route("/login", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST']) 
def home(): 
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data

        result = login_user(username, password) 

        if result["status"] == "access granted":
            session['user_id'] =  result['user_id']
            return redirect(url_for('for_you')) 
        else:
            print(f"LOGIN FAILED WITH STATUS {result['status']}")
            # No redirect, stay on the login page to show error

    return render_template("login.html", form=form)

# ---------- NAVIGATION ----------

@app.route("/search")
def search():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        #session['user_id'] = MOCK_USER_ID # TEMPORARY
    return render_template("search.html")



@app.route("/for_you")
def for_you():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        #session['user_id'] = MOCK_USER_ID # TEMPORARY
    location = session.get('user_location', 'New York')
    # Get user events and use Gemini to tag
    user_id =session['user_id']
    send_event_reminders(user_id)
    user_events = get_user_events()
    for ue in user_events:
        title = ue.get('title', '')
        desc = ''
        tag = gemini_tag(title, desc)
        ue['tag'] = tag
        ue['source'] = 'user'
        ue['title'] = title
        ue['date'] = ue.get('event_time', '')
        ue['description'] = desc
        ue['address'] = ue.get('location', '')
        ue['link'] = ''
        ue['image'] = '/static/img/logo.png'  # Placeholder or user-uploaded image if available

    # Get Google events and add a tag (try to infer from description/title)
    try:
        google_events = get_google_events(location)
    except Exception as e:
        print(f"Error fetching Google events: {e}")
        google_events = []
    for ge in google_events:
        title = ge.get('title', '')
        desc = ge.get('description', '')
        tag = gemini_tag(title, desc)
        ge['tag'] = tag
        ge['source'] = 'google'
        # Flatten date field
        date_val = ge.get('date', '')
        if isinstance(date_val, dict):
            ge['date'] = date_val.get('when') or date_val.get('start_date') or ''
        else:
            ge['date'] = str(date_val)
        # Flatten address field
        addr_val = ge.get('address', '')
        if isinstance(addr_val, list):
            ge['address'] = ', '.join(addr_val)
        else:
            ge['address'] = str(addr_val)
        ge['description'] = desc
        ge['link'] = ge.get('link', ge.get('event_url', ''))
        # Use thumbnail or image if available
        ge['image'] = ge.get('thumbnail') or ge.get('image') or '/static/img/logo.png'

    # Blend and sort events (by date if possible)
    all_events = user_events + google_events
    def event_sort_key(ev):
        # Always return a string for sorting, fallback to empty string if date missing
        date_val = ev.get('date', '')
        if date_val is None:
            return ''
        return str(date_val)
    all_events.sort(key=event_sort_key)
    return render_template("for_you.html", events=all_events)

@app.route('/about')
def about():
    return render_template('about.html')

# ---------- SAVED EVENTS FUNCTIONALITY ----------

@app.route('/api/save_event', methods=['POST'])
def api_save_event():
    if 'user_id' not in session:
        return jsonify({"status": "fail", "message": "User not logged in."}), 401
    user_id = session['user_id']
    event_data = request.json

    if not event_data:
        return jsonify({"status": "fail", "message": "No event data provided."}), 400

    result = save_event(user_id, event_data)
    if result['status'] == 'success':
        return jsonify({"status": "success", "message": result.get('message', "Event saved successfully!")}), 200
    else:
        return jsonify({"status": "fail", "message": result.get('message', "Failed to save event.")}), 400


@app.route('/api/delete_saved_event', methods=['POST'])
def api_delete_saved_event():
    if 'user_id' not in session:
        return jsonify({"status": "fail", "message": "User not logged in."}), 401

    user_id = session['user_id']
    event_global_id = request.json.get('global_id')

    if not event_global_id:
        return jsonify({"status": "fail", "message": "No event global_id provided for deletion."}), 400

    result = delete_saved_event(user_id, event_global_id)
    if result['status'] == 'success':
        return jsonify({"status": "success", "message": result.get('message', "Event removed successfully!")}), 200
    else:
        return jsonify({"status": "fail", "message": result.get('message', "Failed to remove event.")}), 400

@app.route('/api/saved_events', methods=['GET'])
def api_saved_events():
    #user_id = MOCK_USER_ID
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401
    #if not user_id:
    user_id=session['user_id']
    try:
        saved_events = db.get_saved_events(user_id)
        # Assuming db.get_saved_events exists
        return jsonify({'status':'success','events':saved_events}),200
    except:
        print(" error fetching")
        return jsonify({'status':'failed','message':'Error fetching save events'}),500

    return jsonify({'events': saved_events})

# ---------- FETCH API DATA ----------

@app.route("/api/events")
def api_events():
    location = request.args.get("location", "").strip()
    term = request.args.get("interests", "")
    if not location:
        return jsonify({"error": "location is required"}), 400

    try:
        raw_events = search_all_events(location, term)
        
        data_to_send = {"events": raw_events} 
        
        print("Data from search_all_events (wrapped):", data_to_send) 
        return jsonify(data_to_send) 
    except Exception as e:
        print(f"Error in api_events: {e}")
        return jsonify({"error" : str(e)}), 502
def send_event_reminders(user_id):
    now = datetime.now(timezone.utc)
    one_hour_later = now + timedelta(hours=1)
    ten_mins_later = now + timedelta(minutes=10)

    conn = sqlite3.connect("user_info.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, u.email, u.phone, e.event_title, e.event_date, e.event_location, e.event_url, e.reminder_sent, e.sms_sent
        FROM saved_events e
        JOIN users u ON u.id = e.user_id
        WHERE e.user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()

    for event_id, email, phone, title, event_date, location, url, reminder_sent, sms_sent in rows:
        if not event_date:
            continue

        try:
            event_dt = datetime.fromisoformat(event_date)
            if event_dt.tzinfo is None:
                event_dt = event_dt.replace(tzinfo=timezone.utc)

            # 1. Email reminder (1 hour before)
            if reminder_sent == 0 and now < event_dt <= one_hour_later:
                subject = f"Reminder: {title} starts in 1 hour"
                body = f"""
Hello!

Your event "{title}" starts in 1 hour.

Location: {location}
Event Link: {url if url else 'No link available'}

Thank you,
Nom Nom Me Team
                """
                send_email(email, subject, body)
                cursor.execute("UPDATE saved_events SET reminder_sent = 1 WHERE id = ?", (event_id,))
                conn.commit()

            # 2. SMS reminder (10 minutes before)
            if sms_sent == 0 and now < event_dt <= ten_mins_later and phone:
                sms_body = f"Reminder: '{title}' starts in 10 minutes at {location}."
                send_sms(phone, sms_body)
                cursor.execute("UPDATE saved_events SET sms_sent = 1 WHERE id = ?", (event_id,))
                conn.commit()

        except ValueError:
            print(f"Invalid date format for event: {title}")

    conn.close()
    """
    #now = datetime.utcnow()
    one_hour_later = now + timedelta(hours=1)

    conn = sqlite3.connect("user_info.db")
    cursor = conn.cursor()
    cursor.execute("""
        #SELECT e.id, u.email, e.event_title, e.event_date, e.event_location, e.event_url, e.reminder_sent
        #FROM saved_events e
        #JOIN users u ON u.id = e.user_id
        #WHERE e.user_id = ?
    """, (user_id,))
    rows = cursor.fetchall() 

    for event_id, email, title, event_date, location, url, reminder_sent in rows:
        if event_date and reminder_sent == 0:
            try:
                event_dt = datetime.fromisoformat(event_date)
                if now < event_dt <= one_hour_later:
                    subject = f"Reminder: {title} starts in 1 hour"
                    body = f"""
#Hello!

#Your event "{title}" starts in 1 hour.

#ocation: {location}
#Event Link: {url if url else 'No link available'}

#Thank you,
#Nom Nom Me Team
"""
                    send_email(email, subject, body)
                    cursor.execute("UPDATE saved_events SET reminder_sent = 1 WHERE id = ?", (event_id,))
                    conn.commit()
            except ValueError:
                print(f"Invalid date format for event: {title}")

    conn.close()     
"""

if __name__ == "__main__":
    app.run(debug=True)


# PERSONAL NOTES FOR ANNIE: 
# main jobs for Flask file: 
    # routing: page navigation 
    # request handling: processing form + api calls
    # response generation: sending HTML pages / JSON data 
    # session management: keeping track of whose logged in 
    # template rendering: combining HTML templates w data 