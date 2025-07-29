from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db import init_auth_db, register_user, login_user, save_event, get_saved_events, delete_saved_event
from forms import RegistrationForm, LoginForm
from apis.event_handler import search_all_events
from apis.user_events import init_user_events_db, add_user_event, get_user_events
from apis.google_events import get_google_events
import google.generativeai as genai
import re

import db
import math
from dotenv import load_dotenv
import os


load_dotenv()  
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Wnv1I6Tsd7')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None

# Jinja2 filter for upscaling Google image URLs
@app.template_filter('upscale_google_img')
def upscale_google_img(url):
    if not url:
        return url
    # Look for Google image URL patterns with =wXXX-hXXX or =sXXX at the end
    # Replace with =w1200-h900 for higher res
    upscale = re.sub(r'=w\d+-h\d+(-[a-z])?', '=w1200-h900', url)
    upscale = re.sub(r'=s\d+(-[a-z])?', '=w1200-h900', upscale)
    return upscale

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
        tag = request.form.get("tag", "other").strip().lower()  # New: get tag from form
        description = request.form.get("description", "").strip()  # Optionally get description
        if not (title and location and event_time and timezone and tag):
            return render_template("post_event.html", error="All fields are required.")
        # Pass tag to add_user_event if supported, else store in description for now
        try:
            add_user_event(title, location, event_time, timezone, tag, description)
        except TypeError:
            # Fallback for legacy add_user_event signature
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
        # Get multiple selected interests from the multi-select dropdown
        interests_list = request.form.getlist('interests')
        if interests_list:
            location = session.get('user_location', '')
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

    # fetch user events and use stored tag/description, filter by user city
    user_events = get_user_events()
    # City to (lat, lon) lookup for major US cities
    city_coords = {
        'new york': (40.7128, -74.0060),
        'los angeles': (34.0522, -118.2437),
        'chicago': (41.8781, -87.6298),
        'houston': (29.7604, -95.3698),
        'phoenix': (33.4484, -112.0740),
        'philadelphia': (39.9526, -75.1652),
        'san antonio': (29.4241, -98.4936),
        'san diego': (32.7157, -117.1611),
        'dallas': (32.7767, -96.7970),
        'san jose': (37.3382, -121.8863)
    }

    def haversine(lat1, lon1, lat2, lon2):
        R = 3958.8  # Earth radius in miles
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    user_city = None
    user_latlon = None
    if location:
        user_city = location.split(',')[0].strip().lower()
        user_latlon = city_coords.get(user_city)

    filtered_user_events = []
    for ue in user_events:
        event_city = ue.get('location', '').split(',')[-1].strip().lower() if ',' in ue.get('location', '') else ue.get('location', '').strip().lower()
        event_latlon = city_coords.get(event_city)
        # If both user and event have coordinates, filter by distance (<= 50 miles)
        if user_latlon and event_latlon:
            dist = haversine(user_latlon[0], user_latlon[1], event_latlon[0], event_latlon[1])
            if dist > 50:
                continue
        elif user_city and user_city not in event_city:
            continue
        ue['tag'] = ue.get('tag', 'other')
        ue['source'] = 'user'
        ue['title'] = ue.get('title', '')
        ue['date'] = ue.get('event_time', '')
        ue['description'] = ue.get('description', '')
        ue['address'] = ue.get('location', '')
        ue['link'] = ''
        ue['image'] = '/static/img/logo.png'
        filtered_user_events.append(ue)

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
        
        # Try to get the best quality image available with multiple fallbacks
        image = None
        
        # Try multiple image fields in order of preference
        for img_field in ['image', 'photo', 'picture', 'thumbnail', 'banner']:
            if ge.get(img_field):
                image = ge.get(img_field)
                break
        
        if image:
            # Try to get higher resolution version if it's a Google image
            if 'googleusercontent.com' in str(image):
                # Try multiple resolution attempts
                original_image = str(image)
                # First attempt: very high resolution
                image = original_image.replace('=w120-h120-p', '=w2000-h1200-p')
                image = image.replace('=s120', '=s2000')
                image = image.replace('=w120', '=w2000')
                image = image.replace('=h120', '=h1200')
                image = image.replace('=w120-h120', '=w2000-h1200')
                image = image.replace('=s120-c', '=s2000-c')
                # Remove any remaining size restrictions
                image = image.replace('=w120', '=w2000')
                image = image.replace('=h120', '=h1200')
                image = image.replace('=s120', '=s2000')
            elif 'lh3.googleusercontent.com' in str(image):
                # For Google Photos, try to get original size
                image = str(image).replace('=s120', '=s0')
                image = str(image).replace('=w120', '=w0')
                image = str(image).replace('=h120', '=h0')
            elif 'maps.googleapis.com' in str(image):
                # For Google Maps images, try to get higher resolution
                image = str(image).replace('size=120x120', 'size=1200x800')
                image = str(image).replace('zoom=15', 'zoom=18')
            
            ge['image'] = image
        else:
            # If no image found, try to generate a placeholder based on event type
            if 'music' in tag.lower() or 'concert' in title.lower():
                ge['image'] = 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200&h=800&fit=crop&q=90'
            elif 'food' in tag.lower() or 'restaurant' in title.lower():
                ge['image'] = 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&h=800&fit=crop&q=90'
            elif 'sport' in tag.lower() or 'fitness' in title.lower():
                ge['image'] = 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&h=800&fit=crop&q=90'
            else:
                ge['image'] = 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&h=800&fit=crop&q=90'

    # Combine all events (only user events in user's city)
    all_events = filtered_user_events + google_events

    # --- BATCHING LOGIC: 5 events per batch, 70% from liked tags (weighted), 30% from unliked tags ---
    import random
    BATCH_SIZE = 5
    LIKE_RATIO = 0.7
    batch_num = int(request.args.get('batch', 1))
    user_liked_tags = {tag: count for tag, count in user_prefs.items() if count > 0}
    unliked_tags = set([e.get('tag', 'other') for e in all_events]) - set(user_liked_tags.keys())

    # Partition events by tag
    tag_to_events = {}
    for event in all_events:
        tag = event.get('tag', 'other')
        tag_to_events.setdefault(tag, []).append(event)

    # Calculate how many liked/unliked events per batch
    num_liked = round(BATCH_SIZE * LIKE_RATIO)
    num_unliked = BATCH_SIZE - num_liked

    # Weighted selection for liked tags
    liked_tag_total = sum(user_liked_tags.values())
    liked_tag_weights = {tag: (count / liked_tag_total) if liked_tag_total > 0 else 0 for tag, count in user_liked_tags.items()}

    # Flatten all events in a deterministic order for batching
    all_batch_events = []
    used_indices = set()
    total_batches = 0
    while True:
        liked_events = []
        liked_tags = list(user_liked_tags.keys())
        for _ in range(num_liked):
            if not liked_tags:
                break
            tag = random.choices(liked_tags, weights=[liked_tag_weights[t] for t in liked_tags], k=1)[0]
            if tag_to_events.get(tag):
                liked_events.append(tag_to_events[tag].pop(0))
            else:
                liked_tags.remove(tag)
        unliked_events = []
        unliked_tags_list = list(unliked_tags)
        random.shuffle(unliked_tags_list)
        for tag in unliked_tags_list:
            if tag_to_events.get(tag):
                unliked_events.append(tag_to_events[tag].pop(0))
            if len(unliked_events) >= num_unliked:
                break
        batch_events = liked_events + unliked_events
        if len(batch_events) < BATCH_SIZE:
            remaining = []
            for evs in tag_to_events.values():
                remaining.extend(evs)
            random.shuffle(remaining)
            batch_events += remaining[:BATCH_SIZE - len(batch_events)]
        if not batch_events:
            break
        random.shuffle(batch_events)
        all_batch_events.extend(batch_events)
        total_batches += 1
        if sum(len(evs) for evs in tag_to_events.values()) == 0:
            break

    # Serve the correct batch
    start_idx = (batch_num - 1) * BATCH_SIZE
    end_idx = start_idx + BATCH_SIZE
    batch_to_show = all_batch_events[start_idx:end_idx]

    # For frontend: let it know if more batches exist
    more_batches = end_idx < len(all_batch_events)

    return render_template("for_you.html", events=batch_to_show, preferences=prefs, batch=batch_num, more_batches=more_batches)

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

@app.route('/api/liked_events', methods=['GET'])
def api_liked_events():
    if 'user_id' not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 401

    user_id = session['user_id']
    liked_events = db.get_liked_events(user_id)
    return jsonify({'status': 'success', 'events': liked_events}), 200

@app.route('/api/posted_events', methods=['GET'])
def api_posted_events():
    if 'user_id' not in session:
        return jsonify({'status': 'fail', 'message': 'User not logged in.'}), 401

    user_id = session['user_id']
    posted_events = db.get_events_posted_by_user(user_id)
    return jsonify({'status': 'success', 'events': posted_events}), 200

if __name__ == "__main__":
    app.run(debug=True)


# PERSONAL NOTES FOR ANNIE: 
# main jobs for Flask file: 
    # routing: page navigation 
    # request handling: processing form + api calls
    # response generation: sending HTML pages / JSON data 
    # session management: keeping track of whose logged in 
    # template rendering: combining HTML templates w data 