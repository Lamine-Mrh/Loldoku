from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Set up database URI (adjust if needed for your setup)
if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']  # Heroku PostgreSQL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///champions.db'  # SQLite for local testing

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the models

class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    champions = db.relationship('Champion', secondary='champion_region', back_populates='regions')

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    champions = db.relationship('Champion', secondary='champion_role', back_populates='roles')

class Subclass(db.Model):
    __tablename__ = 'subclass'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    champions = db.relationship('Champion', secondary='champion_subclass', back_populates='subclasses')

class Specie(db.Model):
    __tablename__ = 'specie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    champions = db.relationship('Champion', secondary='champion_specie', back_populates='species')

class Champion(db.Model):
    __tablename__ = 'champion'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    release_year = db.Column(db.String(50))
    resource_type = db.Column(db.String(50))
    range = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    champion_type = db.Column(db.String(50))

    # Many-to-many relationships
    regions = db.relationship('Region', secondary='champion_region', back_populates='champions')
    roles = db.relationship('Role', secondary='champion_role', back_populates='champions')
    subclasses = db.relationship('Subclass', secondary='champion_subclass', back_populates='champions')
    species = db.relationship('Specie', secondary='champion_specie', back_populates='champions')

# Association tables for many-to-many relationships
champion_region = db.Table('champion_region',
    db.Column('champion_id', db.Integer, db.ForeignKey('champion.id')),
    db.Column('region_id', db.Integer, db.ForeignKey('region.id'))
)

champion_role = db.Table('champion_role',
    db.Column('champion_id', db.Integer, db.ForeignKey('champion.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

champion_subclass = db.Table('champion_subclass',
    db.Column('champion_id', db.Integer, db.ForeignKey('champion.id')),
    db.Column('subclass_id', db.Integer, db.ForeignKey('subclass.id'))
)

champion_specie = db.Table('champion_specie',
    db.Column('champion_id', db.Integer, db.ForeignKey('champion.id')),
    db.Column('specie_id', db.Integer, db.ForeignKey('specie.id'))
)

# Helper function to get or create an instance
def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
    return instance

# Create all tables in the database if they don't exist
def create_tables():
    with app.app_context():
        db.create_all()


@app.route('/')
def index():
    return render_template('index.html')
# Search route to handle champion search
@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        # Query champions in the database that match the query (case insensitive)
        champions = Champion.query.filter(Champion.name.ilike(f"%{query}%")).all()
        champion_names = [champion.name for champion in champions]
        return jsonify(champion_names)
    return jsonify([])  # Return empty list if no query

# Helper function to get a champion by name
def get_champion_by_name(name):
    return Champion.query.filter_by(name=name).first()

@app.route('/getChampData', methods=['GET'])
def get_champ_data():
    champion_name = request.args.get('name')  # Get the champion's name from the query string
    if not champion_name:
        return jsonify({'error': 'Champion name is required'}), 400  # Return error if no name is provided

    # Query the champion by name
    champion = Champion.query.filter_by(name=champion_name).first()
    if not champion:
        return jsonify({'error': f"Champion '{champion_name}' not found in the database"}), 404

    # Prepare the champion data to return
    champion_data = {
        'name': champion.name,
        'release_year': champion.release_year,
        'resource_type': champion.resource_type,
        'range': champion.range,
        'gender': champion.gender,
        'region': [region.name for region in champion.regions],
        'role': [role.name for role in champion.roles],
        'subclass': [subclass.name for subclass in champion.subclasses],
        'specie': [specie.name for specie in champion.species],
        'champion_type': champion.champion_type
    }

    return jsonify(champion_data)

@app.route('/validate', methods=['POST'])
def validate_input():
    data = request.get_json()

    # Extract values from the request body
    row_attr = data.get('row_attr')
    col_attr = data.get('col_attr')
    row_a = data.get('row_a')
    col_a = data.get('col_a')
    champion_name = data.get('champion_name')
    expected_value_row = data.get('expected_value_row')
    expected_value_col = data.get('expected_value_col')

    # Ensure that all required parameters are present
    if not row_attr or not col_attr or not champion_name:
        print(f"[ERROR] Missing required fields. row_attr: {row_attr}, col_attr: {col_attr}, champion_name: {champion_name}")
        return jsonify({'valid': False, 'error': 'Missing required fields'}), 400

    # Fetch the champion by name
    champion = get_champion_by_name(champion_name)
    if not champion:
        print(f"[ERROR] Champion '{champion_name}' not found in the database.")
        return jsonify({'valid': False, 'error': 'Champion not found'}), 400


    # Helper function to validate attributes (row and column)
    def validate_attribute(attribute, expected_value, champion, champ_attr_name):
        valid_values = []
        # Determine the valid values for the attribute based on the champion data
        if attribute == 'region':
            valid_values = [region.name for region in champion.regions]
            if expected_value == "Runeterra":
                print(f"[DEBUG] '{expected_value}' matches all regions for champion '{champion.name}'.")
                return True, None
        elif attribute == 'role':
            valid_values = [role.name for role in champion.roles]
        elif attribute == 'subclass':
            valid_values = [subclass.name for subclass in champion.subclasses]
        elif attribute == 'specie':
            valid_values = [specie.name for specie in champion.species]
        elif attribute == 'release_year':
            valid_values = [champion.release_year]
        elif attribute == 'resource_type':
            valid_values = [champion.resource_type]
        elif attribute == 'range':
            valid_values = [champion.range]
        elif attribute == 'gender':
            valid_values = [champion.gender]
        elif attribute == 'champion_type':
            valid_values = [champion.champion_type]
        
        print(f"[DEBUG] Valid values for '{champ_attr_name}' of champion '{champion.name}': {valid_values}")

        # Validate the expected value against the valid values
        if expected_value not in valid_values:
            print(f"[ERROR] Invalid {champ_attr_name}. Expected: {expected_value}, Found: {valid_values}")
            return False, f"Invalid {champ_attr_name}. Expected: {expected_value}, Found: {valid_values}"
        return True, None

    # Validate row_attr and col_attr
    is_valid_row, row_error = validate_attribute(row_a, expected_value_row, champion, "row_attr")
    is_valid_col, col_error = validate_attribute(col_a, expected_value_col, champion, "col_attr")

    # Combine errors
    errors = []
    if row_error:
        errors.append(row_error)
    if col_error:
        errors.append(col_error)

    # Return final validation result
    if is_valid_row and is_valid_col:
        print(f"[DEBUG] Champion '{champion_name}' validation PASSED.")
    else:
        print(f"[DEBUG] Champion '{champion_name}' validation FAILED with errors: {errors}")

    return jsonify({'valid': is_valid_row and is_valid_col, 'errors': errors})




# Run the Flask app
if __name__ == '__main__':
    create_tables()  # Create tables if they don't exist
    #app.run(debug=True)
