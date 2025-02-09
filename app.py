from flask import Flask, request, render_template, redirect, url_for, session, flash
"""
Flask: The core class for creating a Flask web application.
request: Handles incoming HTTP requests (e.g., form submissions, query parameters).
render_template: Renders HTML templates dynamically with data.
redirect: Redirects users to a different URL.
url_for: Generates URLs for specific Flask routes.
session: Stores user session data (e.g., login credentials, preferences).
flash: Displays temporary messages (e.g., success or error messages).
"""
import numpy as np
"""numpy: A powerful library for numerical computing, often used for handling arrays, performing mathematical operations, and working with machine learning models."""
import pickle
""""pickle: Used to load and save Python objects, commonly used for saving trained machine learning models and reloading them later."""
from werkzeug.security import generate_password_hash, check_password_hash
"""generate_password_hash(): Converts plain text passwords into hashed versions for secure storage.
check_password_hash(): Verifies if a given plain-text password matches a stored hashed password.
"""
app = Flask(__name__)
app.secret_key = 'your_secret_key'
"""Flask(__name__) initializes the app.
secret_key is used for encrypting session data and enabling features like flash() messages.
"""
# Mock user database
users = {}
"""Users Dictionary: Temporarily stores user credentials (use a database in production).
"""
# Load your pre-trained models and scalers
model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
"""Pickle is used to deserialize pre-trained models and scalers.
StandardScaler (sc) → Standardizes data (zero mean, unit variance).
MinMaxScaler (mx) → Normalizes data (scales values between 0 and 1).
"""
@app.route('/')
def home():
    return redirect(url_for('register'))  # Redirect to register page on startup
"""
@app.route('/') → Maps the root URL (/) to the home function.
redirect(url_for('register')) → Automatically redirects users to the register page.
url_for('register') → Dynamically generates the URL for the register function.
"""
@app.route('/register', methods=['GET', 'POST'])

def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))

        users[username] = generate_password_hash(password)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in users or not check_password_hash(users[username], password):
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))

        session['username'] = username
        flash('Logged in successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' not in session:
        flash('You must log in to access this feature.', 'danger')
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route("/predict", methods=['POST'])
def predict():
    if 'username' not in session:
        flash('You must log in to access this feature.', 'danger')
        return redirect(url_for('login'))

    N = request.form['Nitrogen']
    P = request.form['Phosphorus']
    K = request.form['Potassium']
    temp = request.form['Temperature']
    humidity = request.form['Humidity']
    ph = request.form['pH']
    rainfall = request.form['Rainfall']

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    single_pred = np.array(feature_list).reshape(1, -1)

    mx_features = mx.transform(single_pred)
    sc_mx_features = sc.transform(mx_features)
    prediction = model.predict(sc_mx_features)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = f"{crop} is the best crop to be cultivated right there."
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."

    return render_template('index.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)
