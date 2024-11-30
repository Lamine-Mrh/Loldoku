import csv
import logging
from app import db, Champion, Region, Role, Subclass, Specie, get_or_create, app

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Drop and create tables (run only once, before importing data)
with app.app_context():
    try:
        logger.debug("Dropping all tables...")
        db.drop_all()  # Drop all tables (use cautiously)
        logger.debug("Tables dropped.")
        
        logger.debug("Creating all tables...")
        db.create_all()  # Create all tables as per the model definitions
        logger.debug("Tables created.")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")

# Function to import champions from CSV file
def import_champions_from_csv(filename):
    try:
        with app.app_context():  # Ensure this runs within the app context
            with open(filename, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    logger.debug(f"Processing champion: {row['name']}")
                    
                    # Split comma-separated values into lists
                    regions = [r.strip() for r in row['region'].split(',')]
                    roles = [r.strip() for r in row['role'].split(',')]
                    subclasses = [r.strip() for r in row['subclass'].split(',')]
                    species = [r.strip() for r in row['specie'].split(',')]

                    # Get or create the related entries for region, role, subclass, and specie
                    logger.debug(f"Fetching or creating regions: {regions}")
                    region_objects = [get_or_create(Region, name=region) for region in regions]
                    
                    logger.debug(f"Fetching or creating roles: {roles}")
                    role_objects = [get_or_create(Role, name=role) for role in roles]
                    
                    logger.debug(f"Fetching or creating subclasses: {subclasses}")
                    subclass_objects = [get_or_create(Subclass, name=subclass) for subclass in subclasses]
                    
                    logger.debug(f"Fetching or creating species: {species}")
                    specie_objects = [get_or_create(Specie, name=specie) for specie in species]

                    # Create and add champion to the database
                    champion = Champion(
                        name=row['name'].strip(),
                        release_year=row['release_year'],
                        resources=row['resources'],
                        range=row['range'],
                        gender=row['gender']
                    )

                    # Add the relationships (many-to-many associations)
                    logger.debug(f"Associating regions, roles, subclasses, and species with champion: {champion.name}")
                    champion.regions.extend(region_objects)
                    champion.roles.extend(role_objects)
                    champion.subclasses.extend(subclass_objects)
                    champion.species.extend(specie_objects)

                    db.session.add(champion)

                db.session.commit()
                logger.debug(f"Successfully imported champions from {filename}.")
    except Exception as e:
        logger.error(f"Error during champion import: {e}")
        db.session.rollback()

# Run the import function
if __name__ == '__main__':
    logger.debug("Starting champion import...")
    import_champions_from_csv('champions.csv')
    logger.debug("Champion import completed.")
