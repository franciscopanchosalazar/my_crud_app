import mysql.connector # Driver that allows Python to talk to your MySQL database
from dotenv import load_dotenv # Used to bring the private info from my server into this file (enviroment variables)
import os # Lets us access those variables in Python
from flask import Flask, request, jsonify # Web framework, reads incoming data, converts Python dictionaries into JSON responses for the client 

# Reads the .env file and makes those values available to the program. (the variables will not be pushed into GitHub)
load_dotenv()

# Creates the Flask application object, __name__ tells Flask where to look for resources.
app = Flask(__name__) 

# Connect to mysql using credentials stored in .env
# mysql.connector.connect will always ask for host, user, password and database
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# Defines a Flask route at /add_service.
# It only accepts POST requests, A POST request is used when the client wants to send data to the server.
# When someone sends data to this URL, the function add_service() runs.

@app.route('/add_service', methods=['POST'])

def add_service():
    # The cursor is what we use to execute SQL commands like INSERT, SELECT, UPDATE, DELETE.
    cursor = db.cursor()
    # Reads the incoming JSON body from the request.
    data = request.json
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

# ------------------------------------------------------------------------------------------------------------------------------

# Gets data from a flask route
@app.route('/services', methods=['GET'])

def get_services():
    cursor = db.cursor()
    sql_query = """SELECT * FROM equipment_service""" 
    cursor.execute(sql_query)
    rows = cursor.fetchall()

    # Extracts the column names from the query result.
    columns = [desc[0] for desc in cursor.description]

    # Map each row (tuple) into a dictionary with column names
    result = []
    for row in rows:
        # zip pairs the rows and columns by index, so if you get confused in the future, just google how do this line
        # know what to pair?
        result.append(dict(zip(columns, row)))

    return jsonify(result)

# ------------------------------------------------------------------------------------------------------------------------------

# <int:id> captures which record to update
@app.route('/services/<int:id>', methods=['PUT'])

def update_service(id): # Here the id will come from <int:id>
    # Reads the JSON body sent in the request (request is a flask method), 
    # so if we send { "status": "Complete" }, that will be storaged in the data variable
    data = request.json 
    
    # Updates the matching row in the database.
    cursor = db.cursor()
    sql_query = "UPDATE equipment_service SET status=%s WHERE id=%s"

    # Example: If data['status'] = "Complete" and id = 2, the values will be replaced in the following line
    cursor.execute(sql_query, (data['status'], id))
    db.commit()

    return jsonify({"message": "Service updated"})
