from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#list of all the headers for sql database
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(50))
    department = db.Column(db.String(50))
    job_title = db.Column(db.String(50))
    email_address = db.Column(db.String(50))
    email_address_2 = db.Column(db.String(50))
    business_phone = db.Column(db.String(20))
    mobile_phone = db.Column(db.String(20))
    business_fax = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    business_address = db.Column(db.String(100))
    business_city = db.Column(db.String(50))
    business_state = db.Column(db.String(50))
    business_zip = db.Column(db.String(20))
    business_country = db.Column(db.String(50))
    web_page = db.Column(db.String(100))
    meet_date = db.Column(db.String(50))
    notes = db.Column(db.Text)
