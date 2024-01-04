import unittest
from flask_testing import TestCase
from app import app, db, Contact

class TestBase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()
        sample_contact1 = Contact(
            tag='Contact List',
            first_name='ROLANDAS PRIDOTKAS',
            company='UAB Mobile Center',
            email_address='r.pridotkas@mobilecenter.It',
            business_phone='+370 645 08404',
            business_address='Veterinary st. 44, Biruliskes,LT-54469 Kaunas r., Lituania',
            business_country='Lituania',
            web_page='http://www.mobilecenter.lt'
        )
        sample_contact2 = Contact(
            tag='Contact List',
            first_name='Faisal K',
            company='Supertech Computer Trading LLC',
            job_title='General Manager',
            email_address='faisal@supertechuae.com',
            business_phone='+971 4 327 5554',
            mobile_phone='+971 50 324 8695',
            business_address='P.O.Box: 242167, Dubai - U.A.E.',
            business_city='Dubai',
            business_state='Dubai',
            business_country='Dubai'
        )
        db.session.add(sample_contact1)
        db.session.add(sample_contact2)
        db.session.commit()

        self.contact1_id = sample_contact1.id
        self.contact2_id = sample_contact2.id

        #login
        self.client.post('/login', data=dict(
            username="ani",
            password="ani"
        ), follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestRoutes(TestBase):
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_upload(self):
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)

    def test_upload_convert_csv(self):
        response = self.client.get('/upload_convert_csv')
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)

    def test_search_email(self):
        response = self.client.get('/search_email')
        self.assertEqual(response.status_code, 200)
    
    def test_delete(self):
        # Make a POST request to the delete route
        response = self.client.post(f'/delete/{self.contact1_id}')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after deletion
    
        # Check that the contact was deleted
        contact = Contact.query.get(self.contact1_id)
        self.assertIsNone(contact)

if __name__ == "__main__":
    unittest.main()