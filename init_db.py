from app import app, db
from app import Cause

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have causes
        if Cause.query.count() == 0:
            # Add initial causes
            causes = [
                Cause(name='Education', description='Support educational programs and scholarships'),
                Cause(name='Healthcare', description='Provide medical assistance and healthcare services'),
                Cause(name='Environment', description='Environmental conservation and sustainability initiatives'),
                Cause(name='Poverty Relief', description='Help families in need with basic necessities')
            ]
            
            for cause in causes:
                db.session.add(cause)
            
            db.session.commit()
            print("Database initialized with initial causes!")
        else:
            print("Database already contains causes!")

if __name__ == '__main__':
    init_database()
