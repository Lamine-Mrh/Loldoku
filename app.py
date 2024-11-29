from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///champions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended to disable

db = SQLAlchemy(app)

class Champion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Champion {self.name}>"

@app.route('/')
def index():
    return 'Hello, this is the Loldoku game backend!'

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    row_attr = data.get('row_attr')
    col_attr = data.get('col_attr')
    champion_name = data.get('champion_name')

    # Try to find the champion in the database
    champion = Champion.query.filter_by(name=champion_name).first()

    if champion:
        is_valid = champion.region == row_attr and champion.role == col_attr
        return jsonify({"valid": is_valid})
    else:
        return jsonify({"valid": False})

        
@app.route('/search', methods=['GET'])
def search_champions():
    query = request.args.get('query', '').lower()  # Get the query parameter
    if query:
        # Search for champions whose names start with the query
        matching_champions = Champion.query.filter(Champion.name.ilike(f'{query}%')).all()
        champion_names = [champion.name for champion in matching_champions]
        return jsonify(champion_names)
    return jsonify([])
# Manually create the database tables when needed
def create_db():
    with app.app_context():
        db.create_all()  # Creates the tables

if __name__ == '__main__':
    create_db()  # Ensure the database and tables are created before running the app
    app.run(debug=True)



