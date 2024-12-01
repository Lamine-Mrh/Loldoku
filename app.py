from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Set up database URI (adjust if needed for your setup)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///champions.db'  # SQLite database file
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
    resources = db.Column(db.String(50))
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
        'resource': champion.resources,
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
    row_attr = data.get('row_attr')
    col_attr = data.get('col_attr')
    champion_name = data.get('champion_name')
    expected_value_row = data.get('expected_value_row')
    expected_value_col = data.get('expected_value_col')

    # Fetch the champion
    champion = get_champion_by_name(champion_name)
    if not champion:
        print(f"[DEBUG] Champion '{champion_name}' not found in the database.")
        return jsonify({'valid': False, 'error': 'Champion not found'}), 400

    print(f"[DEBUG] Validating champion '{champion_name}' with attributes: row_attr={row_attr}, col_attr={col_attr}, expected_row={expected_value_row}, expected_col={expected_value_col}")

    is_valid = True
    errors = []

    # Validate based on row_attr
    if row_attr == 'region':
        valid_values = [region.name for region in champion.regions]
        print(f"[DEBUG] Regions for '{champion_name}': {valid_values}")
        if expected_value_row not in valid_values:
            is_valid = False
            errors.append(f"Invalid region. Expected: {expected_value_row}, Found: {valid_values}")

    elif row_attr == 'role':
        valid_values = [role.name for role in champion.roles]
        print(f"[DEBUG] Roles for '{champion_name}': {valid_values}")
        if expected_value_row not in valid_values:
            is_valid = False
            errors.append(f"Invalid role. Expected: {expected_value_row}, Found: {valid_values}")

    elif row_attr == 'subclass':
        valid_values = [subclass.name for subclass in champion.subclasses]
        print(f"[DEBUG] Subclasses for '{champion_name}': {valid_values}")
        if expected_value_row not in valid_values:
            is_valid = False
            errors.append(f"Invalid subclass. Expected: {expected_value_row}, Found: {valid_values}")

    elif row_attr == 'specie':
        valid_values = [specie.name for specie in champion.species]
        print(f"[DEBUG] Species for '{champion_name}': {valid_values}")
        if expected_value_row not in valid_values:
            is_valid = False
            errors.append(f"Invalid specie. Expected: {expected_value_row}, Found: {valid_values}")

    elif row_attr == 'release_year':
        valid_value = champion.release_year
        print(f"[DEBUG] Release year for '{champion_name}': {valid_value}")
        if str(expected_value_row) != str(valid_value):
            is_valid = False
            errors.append(f"Invalid release year. Expected: {expected_value_row}, Found: {valid_value}")

    elif row_attr == 'resources':
        valid_value = champion.resources
        print(f"[DEBUG] Resources for '{champion_name}': {valid_value}")
        if expected_value_row != valid_value:
            is_valid = False
            errors.append(f"Invalid resource. Expected: {expected_value_row}, Found: {valid_value}")

    elif row_attr == 'range':
        valid_value = champion.range
        print(f"[DEBUG] Range for '{champion_name}': {valid_value}")
        if expected_value_row != valid_value:
            is_valid = False
            errors.append(f"Invalid range. Expected: {expected_value_row}, Found: {valid_value}")

    elif row_attr == 'gender':
        valid_value = champion.gender
        print(f"[DEBUG] Gender for '{champion_name}': {valid_value}")
        if expected_value_row != valid_value:
            is_valid = False
            errors.append(f"Invalid gender. Expected: {expected_value_row}, Found: {valid_value}")

    # Validate based on col_attr (similar logic as above)
    # Add the col_attr validation logic here

    # Final result
    if is_valid:
        print(f"[DEBUG] Champion '{champion_name}' validation PASSED.")
    else:
        print(f"[DEBUG] Champion '{champion_name}' validation FAILED with errors: {errors}")

    return jsonify({'valid': is_valid, 'errors': errors})


# Run the Flask app
if __name__ == '__main__':
    create_tables()  # Create tables if they don't exist
    app.run(debug=True)
