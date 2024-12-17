from flask import Flask, flash, session, render_template, redirect
import cgi, os
from flask import Flask, render_template, url_for, redirect, request
from flask import session as login_session
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
import sqlite3
from decimal import Decimal
from flask_admin import Admin, form
from flask import Flask, flash, request, redirect, url_for
import requests
import json
from typing import Union, Type
import os

#from cs50 import SQL
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
#from helpers import apology, passwordValid
#from flask_login import login_required, passwordValid
from flask_login import login_required
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
#import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.config['SECRET_KEY'] = 'this is a secret key'

bcrypt = Bcrypt(app)
DATABASE_PATH = 'C:\\Users\\Bongeka.Mpofu\\DB Browser for SQLite\\site.db'

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# create tables
def create_tables():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

        db.execute('''CREATE TABLE IF NOT EXISTS customer (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               username TEXT,
                               password TEXT,
                               email TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS food (
                                food_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                food_name TEXT NOT NULL,
                                food_price REAL NOT NULL,
                                food_image TEXT)''')
    print("Tables created successfully!")

# Initialize database
#create_tables(DATABASE_PATH)
create_tables()

class Customer:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def save_to_db(self, db_path):
        """Save the customer object to the database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customer (username, email, password)
                VALUES (?, ?, ?)
            ''', (self.username, self.email, self.password))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError as e:
            print(f"Error saving customer to the database: {e}")
            raise ValueError("Username or email already exists.")

#Food class to represent a food item
class Food:
    def __init__(self, food_name, food_price, food_image):
        self.food_name = food_name
        self.food_price = food_price
        self.food_image = food_image

    def save_to_db(self, db_path):
        """Save the food object to the database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO food (food_name, food_price, food_image)
                VALUES (?, ?, ?)
            ''', (self.food_name, self.food_price, self.food_image))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError as e:
            print(f"Error saving food to the database: {e}")
            raise ValueError("Error saving food item.")


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if not username or not email or not password:
            flash("All fields are required!")
            return redirect(url_for('register'))

        # Create and save Customer
        customer = Customer(username, email, hashed_password)
        try:
            customer.save_to_db(DATABASE_PATH)
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error saving customer: {str(e)}")
            print("Error saving customer:", e)
            return redirect(url_for('register'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as db:
            customer = db.execute('SELECT * FROM customer WHERE username = ?', (username,)).fetchone()
            if customer and bcrypt.check_password_hash(customer['password'], password):
                session['username'] = username
                login_session['username'] = username
                print(login_session['username'])
                return redirect(url_for('welcome'))

            else:
                flash("Invalid credentials. Please try again.")
    return render_template('login.html')


@app.route('/welcome')
def welcome():
    if "username" in session:
        with get_db() as db:
            food_items = db.execute('SELECT * FROM food').fetchall()
        return render_template('welcome.html', food=food_items)
    else:
        return redirect(url_for('login'))

@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        food_name = request.form['food_name']
        food_price = float(request.form['food_price'])
        food_image = request.form['food_image']

        if not food_name or not food_price or not food_image:
            flash("All fields are required!")
            return redirect(url_for('add_food'))

        # Create and save Food object
        food_item = Food(food_name, food_price, food_image)
        try:
            food_item.save_to_db(DATABASE_PATH)
            flash("Food item added successfully!")
            return redirect(url_for('welcome'))
        except Exception as e:
            flash(f"Error saving food: {str(e)}")
            print("Error saving food:", e)
            return redirect(url_for('add_food'))

    return render_template('add_food.html')

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)

