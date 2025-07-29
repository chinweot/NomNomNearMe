from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db import init_auth_db, register_user, login_user, save_event, get_saved_events, delete_saved_event
from forms import RegistrationForm, LoginForm
from apis.event_handler import search_all_events
from apis.user_events import init_user_events_db, add_user_event, get_user_events
from apis.google_events import get_google_events
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
MOCK_USER_ID = 1
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
            session['user_id'] = MOCK_USER_ID 
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
            # Get location from session
            location = session.get('user_location', '')
            # Convert interests string to list (comma-separated)
            interests_list = [interest.strip() for interest in interests.split(',') if interest.strip()]
            # Save to database
            db.save_user_preferences(session['user_id'], location, interests_list)
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
            session['user_id'] = MOCK_USER_ID
            return redirect(url_for('for_you')) 
        else:
            print(f"LOGIN FAILED WITH STATUS {result['status']}")
            # No redirect, stay on the login page to show error

    return render_template("login.html", form=form)

# ---------- NAVIGATION ----------

@app.route("/search")
def search():
    if 'user_id' not in session:
        session['user_id'] = MOCK_USER_ID # TEMPORARY
    return render_template("search.html")

#@app.route("/for_you")
#def for_you():
#    if 'user_id' not in session:
#        session['user_id'] = MOCK_USER_ID # TEMPORARY
#    return render_template("for_you.html")


@app.route('/about')
def about():
    return render_template('about.html')

# ---------- SAVED EVENTS FUNCTIONALITY ----------

@app.route('/api/save_event', methods=['POST'])
def api_save_event():
    if 'user_id' not in session:
        return jsonify({"status": "fail", "message": "User not logged in."}), 401
    user_id = MOCK_USER_ID
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

    user_id = MOCK_USER_ID
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
    user_id = MOCK_USER_ID
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 401
    saved_events = db.get_saved_events(user_id) 
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
    
#------------- USERS PREFERENCES AND LOCATION ----------


@app.route("/for_you")
def for_you():
    if 'user_id' not in session:
        return redirect(url_for("home"))

    prefs = db.get_user_preferences(session['user_id'])
    if not prefs:
        return redirect(url_for("onboarding_location"))

    location = prefs["location"]
    user_prefs = prefs["preferences"]

    # fetch and tag user events TEMPORARY
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
        ue['image'] = '/static/img/logo.png'

    # Fetch and tag api events
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

        date_val = ge.get('date', '')
        ge['date'] = date_val.get('when') if isinstance(date_val, dict) else str(date_val)
        ge['address'] = ', '.join(ge.get('address', [])) if isinstance(ge.get('address', ''), list) else ge.get('address', '')
        ge['description'] = desc
        ge['link'] = ge.get('link', ge.get('event_url', ''))
        ge['image'] = ge.get('thumbnail') or ge.get('image') or '/static/img/logo.png'

    # Combine
    all_events = user_events + google_events

    # Score based on prefs
    def score_event(event):
        score = 0
        tags = event.get('tag', '').split(",") 
        for tag in tags:
            tag = tag.strip().lower()
            score += user_prefs.get(tag, 0)
        return score

    food_events = [e for e in all_events if e.get('type') == 'food']
    social_events = [e for e in all_events if e.get('type') == 'social']

    def pick_events(events):
        if not events:
            return []
        
        events.sort(key=score_event, reverse=True)
        top_count = max(1, int(len(events) * 0.7))
        top_events = events[:top_count]
        random_events = events[top_count:]
        
        # Only sample if there are random events to sample from
        if random_events:
            sample_size = min(len(random_events), len(events) - top_count)
            if sample_size > 0:
                return top_events + random.sample(random_events, sample_size)
        
        return top_events

    import random
    final_events = []
    max_len = max(len(food_events), len(social_events))

    for i in range(max_len):
        if i < len(food_events):
            final_events.append(food_events[i])
        if i < len(social_events):
            final_events.append(social_events[i])

    final_events = pick_events(final_events)

    return render_template("for_you.html", events=final_events, preferences=prefs)

@app.route('/api/like_event', methods=['POST'])
def api_like_event():
    if 'user_id' not in session:
        return jsonify({"status": "fail", "message": "User not logged in."}), 401

    user_id = session['user_id']
    data = request.json

    event_global_id = data.get('global_id')
    tags = data.get('tags', [])

    if not event_global_id or not tags:
        return jsonify({"status": "fail", "message": "Event ID and tags are required."}), 400

    result = db.like_event(user_id, event_global_id, tags)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)


# PERSONAL NOTES FOR ANNIE: 
# main jobs for Flask file: 
    # routing: page navigation 
    # request handling: processing form + api calls
    # response generation: sending HTML pages / JSON data 
    # session management: keeping track of whose logged in 
    # template rendering: combining HTML templates w data 