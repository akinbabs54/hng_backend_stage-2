#!/usr/bin/python3
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
# Configure the SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off tracking modifications
db = SQLAlchemy(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#db = SQLAlchemy(app)
#with app.app_context():
#    db.create_all()

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

# Helper function to validate input
def validate_input(data):
    return 'name' in data and isinstance(data['name'], str)

# Create a new person
@app.route('/api', methods=['POST'])
def add_person():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'message': 'Name is required'}), 400
    if isinstance(name,str) == False:
        error_response = {'status': 'error', "message": 'Name must be string'}
        return jsonify(error_response), 400
    existing_person = Person.query.filter_by(name=name).first()
    if existing_person is not None:
        error_response = {'status': 'error', 'message': 'Name already exists'}
        return jsonify(error_response), 400
    new_person = Person(name=name)
    db.session.add(new_person)
    db.session.commit()
    save_person = {'id': new_person.id, "name":new_person.name}
    response = {"status": "success",
                'message': 'Person added successfully',
                'data': save_person }
    return jsonify(response), 201

# Get a person by ID
@app.route('/api/<int:user_id>', methods=['GET'])
def get_person(user_id):
    person = Person.query.get_or_404(user_id)
    existing_person = {'id': person.id, "name":person.name}
    response = {"status": "success",
                'data': existing_person }
    return jsonify(response), 200

# Update a person by ID
@app.route('/api/<int:user_id>', methods=['PUT'])
def update_person(user_id):
    person = Person.query.get_or_404(user_id)
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'message': 'Name is required'}), 400
    
    person.name = name
    db.session.commit()
    
    updated_person = {'id': person.id, "name":person.name}
    response = {"status": "success",
                'message': 'Name updated successfully',
                'data': updated_person }
    return jsonify(response), 200

# Delete a person by ID
@app.route('/api/<int:user_id>', methods=['DELETE'])
def delete_person(user_id):
    person = Person.query.get_or_404(user_id)
    db.session.delete(person)
    db.session.commit()
    
    response = {"status": "success",
                'message': 'Person deleted successfully'
                 }
    return jsonify(response), 200

# Get a person by name
@app.route('/api/name/<name>', methods=['GET'])
def get_person_by_name(name):
    person = Person.query.filter_by(name=name).first()
    if person is None:
        return jsonify({'message': 'Person not found'}), 404
    return jsonify({'name': person.name}), 200

@app.route('/api/clear_data', methods=['DELETE'])
def clear_data():
    Person.query.delete()
    db.session.commit()
    
    return jsonify({'message': 'All data cleared successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
