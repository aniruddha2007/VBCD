from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# class Contact(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     email_address = db.Column(db.String(50))
#     email_address_2 = db.Column(db.String(50))
#     business_phone = db.Column(db.String(20))
#     mobile_phone = db.Column(db.String(20))
#     other_phone = db.Column(db.String(20))
#     primary_phone = db.Column(db.String(20))
#     business_fax = db.Column(db.String(20))
#     job_title = db.Column(db.String(50))
#     company = db.Column(db.String(50))
#     business_address = db.Column(db.String(100))
#     business_city = db.Column(db.String(50))
#     business_state = db.Column(db.String(50))
#     business_zip = db.Column(db.String(20))
#     business_country = db.Column(db.String(50))
#     personal_website = db.Column(db.String(100))
#     web_page = db.Column(db.String(100))
#     birthday = db.Column(db.String(20))
#     notes = db.Column(db.Text)
#     tag = db.Column(db.String(50))


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(50))
    job_title = db.Column(db.String(50))
    email_address = db.Column(db.String(50))
    email_address_2 = db.Column(db.String(50))
    business_phone = db.Column(db.String(20))
    mobile_phone = db.Column(db.String(20))
    other_phone = db.Column(db.String(20))
    primary_phone = db.Column(db.String(20))
    business_fax = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    business_address = db.Column(db.String(100))
    business_city = db.Column(db.String(50))
    business_state = db.Column(db.String(50))
    business_zip = db.Column(db.String(20))
    business_country = db.Column(db.String(50))
    personal_website = db.Column(db.String(100))
    web_page = db.Column(db.String(100))
    notes = db.Column(db.Text)
