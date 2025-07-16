from flask import Flask, render_template, request, jsonify
from apis.yelp import search_events

app = Flask(__name__)
# doing the search page for now for presentations 
@app.route("/") 
def home():
    return render_template("search.html")

@app.route("/api/events")
def api_events():
    location = request.args.get("location", "").strip()
    term = request.args.get("interests", "")
    if not location: 
        return jsonify({"error": "location is required"}), 400
    
    try: 
        data = search_events(location, term, radius_m=1600)
        return jsonify(data)
    except Exception as e: 
        return jsonify({"error" : str(e)}), 502
        

if __name__ == "__main__":
    app.run(debug=True)