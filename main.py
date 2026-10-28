import mysql.connector # Allows Python to talk to your MySQL databases
from dotenv import load_dotenv # Used to bring the private info from my server into this file (enviroment variables)
import os # Lets us access those variables in Python

# Web framework, reads data sent by the browser, converts Python dictionaries into JSON responses, Connect Flask to the HTML, 
# The next two help to send the user to another pages after actions, saves users in the session
from flask import Flask, request, jsonify, render_template, redirect, url_for, session 

from datetime import date # I'll use it to ensure the date is shown in the right format (yyyy-mm-dd)
from datetime import datetime

# Used to hash a password, this means that the password created is converted into "random characters (not really random but seems like)"
from werkzeug.security import generate_password_hash, check_password_hash

# Creates the Flask application object, __name__ tells Flask where to look for resources.
app = Flask(__name__)

# Creates a session key
app.secret_key = "my_app_key"

# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/') # Initial route, when opening the app it will go to the url render in the home function
def home():
    # username = session.get("username")  # username takes the value storaged in the session
    # print(session.get("username")) # Used to test.

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template('index.html')
# ------------------------------------------------------------------------------------------------------------------------------

# Reads the .env file and makes those values available to the program. (the variables will not be pushed into GitHub)
load_dotenv()

# Connect to mysql using credentials stored in .env
# mysql.connector.connect will always ask for host, user, password and database
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# ------------------------------------------------------------------------------------------------------------------------------

# SERVICES STUFF
# Defines a Flask route at /add_service.
# It only accepts POST requests, A POST request is used when the client wants to send data to the server.
# When someone sends data to this URL, the function add_service() runs.

@app.route('/add_service', methods=['POST']) # To test use http://127.0.0.1:5000/add_service in postman (unless you already add js)
def add_service():
    try: 
        # Reads the incoming JSON body from the request.
        data = request.json

        # Checks we have all the fields when inserting new data
        required_fields = ["equipment_type", "brand", "model", "serial_number", 
                           "issue_reported", "service_date", "technician", "status"]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing '{field}' in request body"}), 400

        # Checks that the status is allowed by the created database (as I used ENUM in the status column when created)
        # As the options come from a <select> tag in HTML, I don't think I should use ENUM in MySql.
        allowed_statuses = ["Pending", "In Progress", "Completed"]

        if data['status'] not in allowed_statuses:
            return jsonify({"error": f"Invalid status. '{data['status']}' is not a valid status. Must be one of {allowed_statuses}"}), 400

        # The cursor is what we use to execute SQL commands like INSERT, SELECT, UPDATE, DELETE.
        cursor = db.cursor()
        sql_query = """INSERT INTO equipment_service 
                (equipment_type, brand, model, serial_number, issue_reported, service_date, technician, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""" # %s are place holders for the values to insert into the table later

        # Collects the values from the JSON request and puts them into a tuple
        values = (
            data['equipment_type'],
            data['brand'],
            data['model'],
            data['serial_number'],
            data['issue_reported'],
            data['service_date'],
            data['technician'],
            data['status']
        )

        # Executes the SQL command with the provided values
        cursor.execute(sql_query, values)

        # Saves the changes in the data base
        db.commit()

        return jsonify({"message": "Service job added successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------------------------------------------

# Used to retrieve the services page
@app.route('/all_services')
def all_services():
    if "username" not in session:
        return redirect(url_for("login"))
    
    return render_template('services.html')
# ------------------------------------------------------------------------------------------------------------------------------

# Used when pressing the button
@app.route('/get_services', methods=['GET'])
def get_services():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM equipment_service")
        services = cursor.fetchall()

        # Ensure service_date is always a string in YYYY-MM-DD format
        for s in services:
            if s.get("service_date"):
                # If it's already a string, leave it
                if isinstance(s["service_date"], str):
                    s["service_date"] = s["service_date"]
                else:
                    # If it's a date/datetime object, format it
                    s["service_date"] = s["service_date"].strftime("%d-%m-%Y")

        return jsonify(services), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------------------------------------------

# <int:id> captures which record to update
@app.route('/services/<int:id>', methods=['PUT'])
def update_service(id): # Here the id will come from <int:id>
    try:
        # Reads the JSON body sent in the request (request is a flask method), 
        # so if we send { "status": "Completed" }, that will be storaged in the data variable
        data = request.json 

        if not data or 'status' not in data:
            return jsonify({"error": "Missing 'status' in request body"}), 400

        # Checks that the status is allowed by the created database (as I used ENUM in the status column when created)
        allowed_statuses = ["Pending", "In Progress", "Completed"]

        if data['status'] not in allowed_statuses:
            return jsonify({"error": f"Invalid status. '{data['status']}' Is not a valid status. Must be one of {allowed_statuses}"}), 400
        
        # Updates the matching row in the database.
        cursor = db.cursor()
        sql_query = "UPDATE equipment_service SET status=%s WHERE id=%s"

        # Example: If data['status'] = "Completed" and id = 2, the values will be replaced in the following line
        cursor.execute(sql_query, (data['status'], id))
        db.commit()

        if cursor.rowcount == 0:
            # No rows updated → id not found
            return jsonify({"error": f"Service with id {id} not found"}), 404
        
        return jsonify({"message": "Service updated"})

    except Exception as e:
        # Catchs any unexpected database or code error (e)
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/services/<int:id>', methods=['DELETE'])
def delete_service(id):    
    # Catch internal sql errors
    try:
        cursor = db.cursor()
        
        # Delete the matching row in the database.
        sql_query = "DELETE FROM equipment_service WHERE id=%s";    
        
        # The second argument must be a sequence or tuple of values that match the placeholders in the SQL string
        cursor.execute(sql_query, (id,)) 

        # Tells us how many rows were deleted
        if cursor.rowcount == 0:
            return jsonify({"error": "Service not found"}), 404

        db.commit()
        return jsonify({"message": f"Service with id {id} deleted"})

    except Exception as e:
        # Catchs any unexpected database or code error (e)
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------------------------------------------

# USERS STUFF

@app.route('/register' , methods=['GET', 'POST'])
def register():
    if 'username' not in session:   # Ensure that only can access to this option while logged in
        return redirect(url_for('login'))

    if session.get("role") != "admin":  # Only users with admin role can access to register new users
        return "Access denied"

    cursor = db.cursor()
    
    # Checks if the user submitted the form.
    if request.method == "POST":
        username =  request.form["user_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # Hash the password before saving
        hashed_pw = generate_password_hash(password)

        # Used to test
        """
        print("Username:", username)
        print("Email:", email)
        print("Password:", password)
        print("Hashed:", hashed_pw)
        print("Role:", role)
        """

        # Insert into DB (users table)
        sql_query = "INSERT INTO users(user_name, email, password_hash, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (username, email, hashed_pw, role))
        db.commit()

        #return jsonify({"message": "User has been succesfully added"})

        #return redirect(url_for("login"))  # Redirect to login page later
    
    return render_template("register.html")
# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/all_users')
def all_users():
    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":  # Only users with admin role can access to register new users
        return "Access denied"
    
    return render_template('users.html')
# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        return jsonify(users), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):    
    # Catch internal sql errors
    try:
        cursor = db.cursor()
        
        # Delete the matching row in the database.
        sql_query = "DELETE FROM users WHERE id=%s";    
        
        # The second argument must be a sequence or tuple of values that match the placeholders in the SQL string
        cursor.execute(sql_query, (id,)) 

        # Tells us how many rows were deleted
        if cursor.rowcount == 0:
            return jsonify({"error": "Service not found"}), 404

        db.commit()
        return jsonify({"message": f"User with id {id} deleted"})

    except Exception as e:
        # Catchs any unexpected database or code error (e)
        return jsonify({"error": str(e)}), 500
# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/login' , methods=['GET', 'POST'])
def login():
    cursor = db.cursor()

    # Checks the user submitted from the form.
    if request.method == "POST":
        username =  request.form["user_name"]
        password = request.form["password"]

        # Used to tests
        # print("Username:", username) 
        # print("Password:", password)

        # Checks for user existence
        sql_query = "SELECT id, user_name, password_hash, role FROM users WHERE user_name = %s"
        cursor.execute(sql_query, (username,))
        user = cursor.fetchone()

        if user==None:
            print(f"{username} is not a valid user" ) # the print must be changed to do something else while I move on.
        else:
            # Verifies the password
            if user and check_password_hash(user[2], password): # user[2] is the stored hash from the database. 
                # print("Login successful")   # Used to tests

                session["username"] = username # With this line the session will remember the current user.
                session["role"] = user[3] # We can storage the role of the specific user
                return redirect(url_for("home"))
            
            else:
                # Print must be change to do something else when moving on
                print(f"{user[1]} is a valid user but")
                print("Wrong password")

    return render_template("login.html")
# ------------------------------------------------------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    session.pop("username", None) # Removes 'username' from the session if it exists.
    return redirect(url_for("login"))
