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

@app.route('/add_service', methods=['POST']) # To test use http://127.0.0.1:5000/add_service in postman

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

# Gets data from a flask route
@app.route('/services/<int:id>', methods=['GET'])

def get_service(id):
    try:
        cursor = db.cursor(dictionary=True)
        sql_query = "SELECT * FROM equipment_service WHERE id=%s" 
        cursor.execute(sql_query, (id,))
        service_row = cursor.fetchone()

        if not service_row:
            return jsonify({"error": f"Service with id {id} not found"}), 404

        return jsonify(service_row), 200

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
    