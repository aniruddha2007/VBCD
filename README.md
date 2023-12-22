# VBCD

Virtuit Business Card Database Management Project
This is a Flask web application designed for viewing, editing, and managing a database of contacts. The project allows users to perform various operations such as uploading CSV files, searching the database, editing contact information, and more.

Features
Database Management: View and manage contacts in the database.
CSV File Upload: Upload CSV files to populate the database.
Search Functionality: Search for contacts based on various criteria.
User Authentication: Log in and log out functionality with user registration.
Technologies Used
Flask
SQLAlchemy
SQLite
Babel for Internationalization (i18n)
HTML, CSS
Project Structure
app.py: The main Flask application file.
modules/functions.py: Functions for database initialization, login handling, etc.
modules/contacts.py: Contact model definition.
static: Folder for static files such as CSS styles.
templates: HTML templates for different routes.
Getting Started

python app.py
Open your browser and go to http://localhost:5000/ to access the application.

Usage
Home: View and manage contacts in the database.
Upload: Upload CSV files to populate the database.
Search: Search for contacts based on various criteria.
Edit/Delete: Edit or delete individual contacts.
Login/Register: User authentication for secure access.
Configuration
The database is configured to use SQLite by default. You can modify the SQLALCHEMY_DATABASE_URI in app.py to use a different database.
Internationalization (i18n)
The application supports multiple languages. You can change the language by clicking on the language switcher.

License
This project is Private licensed.
