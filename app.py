from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db import init_auth_db, register_user, login_user, save_event, get_saved_events, delete_saved_event
from forms import RegistrationForm, LoginForm
from apis.event_handler import search_all_events
import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Wnv1I6Tsd7'

init_auth_db()
MOCK_USER_ID = 1

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

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data 
        password = form.password.data 

        result = register_user(username, email, password)
        if result['status'] == 'success':
            session['user_id'] = MOCK_USER_ID
            return redirect(url_for('home'))
        else: 
            print(f"REGISTRATION FAILED WITH STATUS {result['status']}")
    
    return render_template("signup.html", form=form)

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
            return redirect(url_for('search')) 
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
    saved_events = db.get_saved_events(user_id) # Assuming db.get_saved_events exists
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
        

if __name__ == "__main__":
    app.run(debug=True)


# PERSONAL NOTES FOR ANNIE: 
# main jobs for Flask file: 
    # routing: page navigation 
    # request handling: processing form + api calls
    # response generation: sending HTML pages / JSON data 
    # session management: keeping track of whose logged in 
    # template rendering: combining HTML templates w data 