# Nom Nom Near Me

**Find delicious free food and social events near you!**

Nom Nom Near Me is a web application that connects students and community members with free food and social events in their area with a personalized for you page . We help you discover and attend events that bring people together through food and community.

---

## Features

- **Smart Search**: Find free food and social events by location and preferences  
- **Personalized For You Feed**: Curated feed based on your interests with events in your area 
- **User Event Posting**: Share your own free food and social events with the community  
- **Save Events**: Keep track of events you're interested in  
- **Community Driven**: Events submitted and reviewed by community members  
- **Responsive Design**: Works seamlessly on desktop
---

## Tech Stack

### Frontend
- HTML5, CSS3, JavaScript  
- [TailwindCSS](https://tailwindcss.com/) 
- Custom CSS animations and effects  

### Backend
- Python [Flask](https://flask.palletsprojects.com/) web framework  
- SQLite database  
- Flask-WTF for forms  

### APIs & Integration
- Google Places API for location services  
- Reddit API for community event discovery  
- Yelp API for restaurant and free food/social event data  
- User event management system  

---

## Team
- **Hamed Diakite** - Backend & Database  
- **Chichi Otti** - Frontend Development  
- **David Pascual** - Backend Development  
- **Gustavo Belaunde** - Backend Development  
- **Iverson Lopez** - Full Stack Development  

---

## Installation

### Prerequisites
- Python 3
- `pip`   
- API Keys for:
  - Google Places API  
  - Reddit API  
  - Yelp API  

---

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nom-nom-near-me.git
   cd nom-nom-near-me
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    pip install python-dotenv
    ```  

4. **Set up environment variables- Create a .env file in the root directory**
    ```bash
    FLASK_APP=app.py
    FLASK_ENV=development
    GOOGLE_API_KEY=your_google_api_key_here
    REDDIT_CLIENT_ID=your_reddit_client_id_here
    REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
    YELP_API_KEY=your_yelp_api_key_here
    YELP_CLIENT_ID=your_yelp_client_id_here
    ```

5. **Run the application**
    ```bash
    flask run 
    ```
    The app will be available at http://localhost:5000