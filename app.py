from flask import Flask, render_template, request, jsonify, redirect, url_for
from db import init_auth_db, register_user, login_user 
from forms import RegistrationForm, LoginForm
from apis.event_handler import search_all_events
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Wnv1I6Tsd7'

init_auth_db()

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
            return redirect(url_for('home'))
        else: 
            print(f"REGISTRATION FAILED WITH STATUS {result.status}")
    
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
            return redirect(url_for('search')) 
        else:
            print(f"LOGIN FAILED WITH STATUS {result['status']}")
            # No redirect, stay on the login page to show error

    return render_template("login.html", form=form)

# ---------- NAVIGATION ----------

@app.route("/search")
def search():
    return render_template("search.html")

@app.route('/about')
def about():
    return render_template('about.html')

# ---------- FETCH API DATA ----------

@app.route("/api/events")
def api_events():
    location = request.args.get("location", "").strip()
    term = request.args.get("interests", "")
    if not location: 
        return jsonify({"error": "location is required"}), 400
    
    try: 
        data = search_all_events(location, term)
        return jsonify(data)
    except Exception as e: 
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