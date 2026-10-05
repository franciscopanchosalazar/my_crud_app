import mysql.connector # Driver that allows Python to talk to your MySQL database
from dotenv import load_dotenv # Used to bring the private info from my server into this file (enviroment variables)
import os # Lets us access those variables in Python
from flask import Flask, request, jsonify # Web framework, reads incoming data, converts Python dictionaries into JSON responses for the client 

# Reads the .env file and makes those values available to the program. (the variables will not be pushed into GitHub)
load_dotenv()

# Creates the Flask application object, __name__ tells Flask where to look for resources.
app = Flask(__name__) 

# Connect to mysql using credentials stored in .env
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# The cursor is what we use to execute SQL commands like INSERT, SELECT, UPDATE, DELETE.
cursor = db.cursor()

# Defines a Flask route at /add_service.
# It only accepts POST requests (used for creating new records).
# When someone sends data to this URL, the function add_service() runs.

@app.route('/add_service', methods=['POST'])

def add_service():
    # Reads the incoming JSON body from the request.
    data = request.json
    sql = """INSERT INTO equipment_service 
             (equipment_type, brand, model, serial_number, issue_reported, service_date, technician, status)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""" # %s are place holders for the values to insert into the table

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
    cursor.execute(sql, values)

    # Saves the changes in the data base
    db.commit()
    
    return jsonify({"message": "Service job added successfully!"})
