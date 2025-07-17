from flask import Flask, render_template, request, jsonify
from apis.yelp import search_events

app = Flask(__name__)

@app.route("/") 
def home():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/api/events")
def api_events():
    location = request.args.get("location", "").strip()
    term = request.args.get("interests", "")
    if not location: 
        return jsonify({"error": "location is required"}), 400
    
    try: 
        data = search_events(location, term)
        return jsonify(data)
    except Exception as e: 
        return jsonify({"error" : str(e)}), 502

if __name__ == "__main__":
    app.run(debug=True)
