from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

app = Flask(__name__, 
    static_url_path='',
    static_folder='static',
    template_folder='templates')

# MySQL configuration
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'charity_db')

# Using pymysql driver with URL encoded password
password = quote_plus(DB_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{password}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Donor(db.Model):
    __tablename__ = 'donors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    donations = db.relationship('Donation', backref='donor', lazy=True)

class Cause(db.Model):
    __tablename__ = 'causes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    donations = db.relationship('Donation', backref='cause', lazy=True)

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id'), nullable=False)
    cause_id = db.Column(db.Integer, db.ForeignKey('causes.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='completed')

with app.app_context():
    db.create_all()

@app.before_request
def log_request_info():
    print('Database URL:', app.config['SQLALCHEMY_DATABASE_URI'])
    print('Headers:', request.headers)
    print('Path:', request.path)

@app.route('/')
def home():
    causes = Cause.query.filter_by(active=True).all()
    return render_template('index.html', causes=causes)

@app.route('/donate', methods=['POST'])
def donate():
    try:
        data = request.json
        
        # Find or create donor
        donor = Donor.query.filter_by(email=data['email']).first()
        if not donor:
            donor = Donor(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', '')
            )
            db.session.add(donor)
            db.session.flush()

        # Get cause
        cause = Cause.query.filter_by(name=data['cause']).first()
        if not cause:
            return jsonify({'error': 'Invalid cause selected'}), 400

        # Create donation
        donation = Donation(
            amount=float(data['amount']),  # Amount in Rupees
            donor_id=donor.id,
            cause_id=cause.id,
            transaction_id=f'TXN_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}_{donor.id}'
        )
        
        db.session.add(donation)
        db.session.commit()
        
        return jsonify({
            'message': 'Donation successful!',
            'transaction_id': donation.transaction_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/donations')
def get_donations():
    donations = Donation.query.order_by(Donation.date.desc()).all()
    donation_list = []
    for donation in donations:
        donation_list.append({
            'id': donation.id,
            'name': donation.donor.name,
            'amount': donation.amount,
            'cause': donation.cause.name,
            'date': donation.date.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_id': donation.transaction_id
        })
    return jsonify(donation_list)

@app.route('/delete_donation/<int:donation_id>', methods=['DELETE'])
def delete_donation(donation_id):
    try:
        donation = Donation.query.get_or_404(donation_id)
        db.session.delete(donation)
        db.session.commit()
        return jsonify({'message': 'Donation deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/causes')
def get_causes():
    causes = Cause.query.filter_by(active=True).all()
    return jsonify([{
        'id': cause.id,
        'name': cause.name,
        'description': cause.description
    } for cause in causes])

@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(debug=True)
