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
    release_year = db.Column(db.Integer)
    resources = db.Column(db.String(50))
    range = db.Column(db.String(50))
    gender = db.Column(db.String(50))

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

@app.route('/validate', methods=['POST'])
def validate_input():
    data = request.get_json()
    row_attr = data.get('row_attr')  # Region (e.g., 'Demacia')
    col_attr = data.get('col_attr')  # Role (e.g., 'Top')
    champion_name = data.get('champion_name')
    expected_value_row = data.get('expected_value_row')  # Expected region (e.g., 'Demacia')
    expected_value_col = data.get('expected_value_col')  # Expected role (e.g., 'Top')

    # Get the champion from the database
    champion = get_champion_by_name(champion_name)
    if not champion:
        print(f"[DEBUG] Champion '{champion_name}' not found in the database.")
        return jsonify({'valid': False, 'error': 'Champion not found'}), 400

    print(f"[DEBUG] Validating champion '{champion_name}' with row: {row_attr}, column: {col_attr}, expected region: {expected_value_row}, expected role: {expected_value_col}")

    # Perform the validation based on the row (region) and column (role) attributes
    is_valid = False

    # Check if the region matches the expected value (row)
    if row_attr == 'region':
        valid_regions = [region.name for region in champion.regions]
        print(f"[DEBUG] Champion '{champion_name}' regions: {valid_regions}. Expected region: {expected_value_row}")
        is_valid = expected_value_row in valid_regions

    # Check if the role matches the expected value (column)
    if col_attr == 'Top' or col_attr == 'Mid' or col_attr == 'Jungle':
        valid_roles = [role.name for role in champion.roles]
        print(f"[DEBUG] Champion '{champion_name}' roles: {valid_roles}. Expected role: {expected_value_col}")
        is_valid = is_valid and expected_value_col in valid_roles  # Both region and role must be valid

    # Print debug info based on validation result
    if is_valid:
        print(f"[DEBUG] Champion '{champion_name}' is valid.")
    else:
        print(f"[DEBUG] Champion '{champion_name}' is NOT valid.")

    return jsonify({'valid': is_valid})



# Run the Flask app
if __name__ == '__main__':
    create_tables()  # Create tables if they don't exist
    app.run(debug=True)
