#imports
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session,
    jsonify,
    flash,
)
from modules.functions import (
    csv_to_db_mapping,
    csv_to_db_mapping_zh,
    load_csv_to_db,
    load_csv,
    init_db,
    login_required,
    check_csv_encoding,
    detect_and_convert_encoding,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, _
from modules.contacts import Contact, db
from io import TextIOWrapper, BytesIO, StringIO
import csv
import sqlite3

# The above code is initializing a Flask app and configuring the database connection.
# Initialize the Flask app
app = Flask(__name__, static_folder="static", static_url_path="")
babel = Babel(app)

# Configure the database connection
app.secret_key = "3LKENMg6RtmEqC9gFY83xsSDMFQffpDYkHnyyCms"
SECRET_PASSWORD = "VIRTUIT"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"
app.config["select_language"] = "english"
db.init_app(app)


def select_language():
    """
    The function returns the value of the "select_language" configuration variable.
    :return: the value of the "select_language" key in the app.config dictionary.
    """
    return app.config["select_language"]


# Homepage route to display the database
    """
    The index function is a route in a Python Flask application that displays the database records based
    on the selected filters.
    :return: the rendered template "index.html" with the contacts variable passed as an argument.
    """
@app.route("/")
@login_required
def index():
    selected_language = select_language()
    filters = {}
    for header in Contact.__table__.columns.keys():
        value = request.args.get(header)
        if value:
            filters[header] = value

    contacts = Contact.query.filter_by(**filters).all()
    return render_template(f"{selected_language}/index.html", contacts=contacts)
    """_summary_

    Returns:
        _type_: _description_
    """



# Upload route for handling CSV file upload
    """
    The `upload` function is a route in a Python Flask application that handles the uploading of a CSV
    file, processes it, and saves the data to a database.
    :return: the rendered template for the upload page.
    """
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    selected_language = select_language()
    if request.method == "POST":
        try:
            uploaded_file = request.files["csvFile"]
            use_chinese_mapping = "chineseCheckbox" in request.form

            # Check if the uploaded file is a CSV file
            if uploaded_file.filename.endswith('.csv'):
                # Use BytesIO to read the content of the file
                csv_content = BytesIO(uploaded_file.read())

                # Convert to TextIOWrapper to handle Unicode BOM in CSV file
                csv_file_wrapper = TextIOWrapper(csv_content, encoding="utf-8")

                # Process and save the data to the database
                load_csv_to_db(csv_file_wrapper, use_chinese_mapping)

                # Commit changes to the database
                db.session.commit()

                flash("File uploaded successfully", "success")
                return redirect("/")
            else:
                flash("Invalid file format. Please upload a CSV file.", "danger")

        except Exception as e:
            flash(f"Error uploading file: {str(e)}", "danger")

    return render_template(f"{selected_language}/upload.html")
    selected_language = select_language()
    if request.method == "POST":
        try:
            uploaded_file = request.files["csvFile"]
            use_chinese_mapping = "chineseCheckbox" in request.form

            # Use TextIOWrapper to handle Unicode BOM in CSV file
            csv_file_wrapper = TextIOWrapper(uploaded_file.stream, encoding="utf-8")
            load_csv_to_db(csv_file_wrapper, use_chinese_mapping)

            # Commit changes to the database
            db.session.commit()

            flash("File uploaded successfully", "success")
            return redirect("/")
        except Exception as e:
            flash(f"Error uploading file: {str(e)}", "danger")

    return render_template(f"{selected_language}/upload.html")


# Upload route for handling CSV file upload
    """
    The function `upload_convert_csv` handles the upload of a CSV file, converts it to UTF-8 format, and
    provides it as a downloadable file.
    :return: a downloadable CSV file.
    """
@app.route("/upload_convert_csv", methods=["GET", "POST"])
@login_required
def upload_convert_csv():
    selected_language = select_language()
    if request.method == "POST":
        uploaded_file = request.files["csvFileSecond"]
        detected_encoding = check_csv_encoding(uploaded_file)

        if detected_encoding.lower() != "utf-8":
            # Convert to UTF-8
            uploaded_file.seek(0)
            utf8_content = detect_and_convert_encoding(uploaded_file.read())
        else:
            # Already UTF-8, no need to convert
            uploaded_file.seek(0)
            utf8_content = uploaded_file.read()

        if utf8_content is not None:
            # Use BytesIO to create a downloadable file
            download_file = BytesIO(utf8_content)
            download_file.seek(0)

            # Provide the file for download
            return send_file(
                download_file,
                mimetype="text/csv",
                as_attachment=True,
                download_name="converted_file.csv",
            )
        else:
            flash("Error converting the file to UTF-8", "error")

    return render_template(f"{selected_language}/upload.html")


# Search route for searching the database
    """
    The `search` function in this Python code is used to perform a search query on a database based on
    user input and display the search results.
    :return: a rendered template for the search results page, passing the contacts and query as
    variables to be used in the template.
    """
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    selected_language = select_language()
    if request.method == "POST":
        query = request.form.get("query")
        # Perform a database query based on the search query
        # Adjust the query based on your search requirements
        contacts = Contact.query.filter(
            (Contact.first_name.like(f"%{query}%"))
            | (Contact.last_name.like(f"%{query}%"))
            | (Contact.email_address.like(f"%{query}%"))
            | (Contact.email_address_2.like(f"%{query}%"))
            | (Contact.business_phone.like(f"%{query}%"))
            | (Contact.job_title.like(f"%{query}%"))
            | (Contact.company.like(f"%{query}%"))
            | (Contact.business_country.like(f"%{query}%"))
            | (Contact.notes.like(f"%{query}%"))
            | (Contact.tag.like(f"%{query}%"))
            | (Contact.meet_date.like(f"%{query}%"))
        ).all()
        return render_template(
            f"{selected_language}/search_results.html", contacts=contacts, query=query
        )
    return render_template(f"{selected_language}/search.html")


# Search only email results
    """
    The `search_email` function in this Python code performs a search query on a database for contacts
    based on an input query, and returns the results in a template.
    :return: a rendered template, either "search_email_results.html" or "search_email.html", depending
    on the request method.
    """
@app.route("/search_email", methods=["GET", "POST"])
@login_required
def search_email():
    selected_language = select_language()
    if request.method == "POST":
        query = request.form.get("query")
        # Perform a database query based on the search query
        # Adjust the query based on your search requirements
        contacts = Contact.query.filter(
            (Contact.first_name.like(f"%{query}%"))
            | (Contact.last_name.like(f"%{query}%"))
            | (Contact.email_address.like(f"%{query}%"))
            | (Contact.email_address_2.like(f"%{query}%"))
            | (Contact.business_phone.like(f"%{query}%"))
            | (Contact.job_title.like(f"%{query}%"))
            | (Contact.company.like(f"%{query}%"))
            | (Contact.business_country.like(f"%{query}%"))
            | (Contact.notes.like(f"%{query}%"))
            | (Contact.tag.like(f"%{query}%"))
            | (Contact.meet_date.like(f"%{query}%"))
        ).all()
        return render_template(
            f"{selected_language}/search_email_results.html",
            contacts=contacts,
            query=query,
        )
    return render_template(f"{selected_language}/search_email.html")


# edit contact
    """
    The `edit` function in this Python code is used to edit a contact's information and update it in the
    database.
    
    :param contact_id: The `contact_id` parameter is the unique identifier of the contact that needs to
    be edited. It is used to retrieve the contact from the database and display its current data in the
    edit form
    :return: the rendered template "edit.html" with the contact data and headers as arguments.
    """
@app.route("/edit/<int:contact_id>", methods=["GET", "POST"])
@login_required
def edit(contact_id):
    selected_language = select_language()
    contact = Contact.query.get_or_404(contact_id)
    print(f"Contact ID: {contact_id}")
    print(f"Contact Data: {contact}")

    # Define headers multi language dictionary
    editable_fields = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "E-mail Address": "email_address",
        "E-mail 2 Address": "email_address_2",
        "Business Phone": "business_phone",
        "Mobile Phone": "mobile_phone",
        "Business Fax": "business_fax",
        "Job Title": "job_title",
        "Company": "company",
        "Business Address": "business_address",
        "Business City": "business_city",
        "Business State": "business_state",
        "Business Postal Code": "business_zip",
        "Business Country/Region": "business_country",
        "Meet Date": "meet_date",
        "Web Page": "web_page",
        "Birthday": "birthday",
        "Notes": "notes",
        "Tag": "tag",
    }

    headers = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "E-mail Address": "email_address",
        "E-mail 2 Address": "email_address_2",
        "Business Phone": "business_phone",
        "Mobile Phone": "mobile_phone",
        "Business Fax": "business_fax",
        "Department": "department",
        "Job Title": "job_title",
        "Company": "company",
        "Business Address": "business_address",
        "Business City": "business_city",
        "Business State": "business_state",
        "Business Postal Code": "business_zip",
        "Business Country/Region": "business_country",
        "Meet Date": "meet_date",
        "Web Page": "web_page",
        "Birthday": "birthday",
        "Notes": "notes",
        "Tag": "tag",
    }

    if request.method == "POST":
        new_values = {}
        # Update contact all fields based on the form data
        for headers, field_name in headers.items():
            new_value = request.form.get(field_name)
            setattr(contact, field_name, new_value)

        # Update other fields as needed
        db.session.commit()
        return redirect("/")

    return render_template(
        f"{selected_language}/edit.html", contact=contact, headers=headers
    )


# delete contact
    """
    This function deletes a contact from the database and redirects to the home page.
    
    :param contact_id: The `contact_id` parameter is the unique identifier of the contact that needs to
    be deleted. It is used to retrieve the contact from the database and perform the deletion operation
    :return: a rendered template for the delete.html file, passing the contact object as a parameter.
    """
@app.route("/delete/<int:contact_id>", methods=["GET", "POST"])
@login_required
def delete(contact_id):
    selected_language = select_language()
    contact = Contact.query.get_or_404(contact_id)

    if request.method == "POST":
        # Delete the contact and redirect to the home page
        db.session.delete(contact)
        db.session.commit()
        return redirect("/")

    return render_template(f"{selected_language}/delete.html", contact=contact)

# Route for deleting selected contacts
    """
    The `delete_selected_contacts` function deletes the contacts with the specified IDs from the
    database and returns a JSON response indicating the success or failure of the operation.
    :return: The route is returning a JSON response. If the deletion is successful, it returns a JSON
    object with the keys 'success' set to True and 'message' set to 'Contacts deleted successfully'. If
    there is an error during the deletion process, it returns a JSON object with the keys 'message' set
    to 'Error deleting contacts', 'success' set to False, and 'error' set to
    """
@app.route('/delete_selected', methods=['POST'])
def delete_selected_contacts():
    try:
        data = request.get_json()
        contact_ids = data.get('contactIds', [])
        
        # Delete contacts from the database
        for contact_id in contact_ids:
            contact = Contact.query.get(contact_id)
            print("Contact IDs to delete:", contact_ids)
            if contact:
                db.session.delete(contact)
            else:
                print(f"Contact ID {contact_id} not found")
        
        # Commit the changes to the database
        db.session.commit()

        return jsonify({'success': True, 'message': 'Contacts deleted successfully'})
    except Exception as e:
        print(f"Error deleting:{str(e)}")
        return jsonify({'message':'Error deleting contacts', 'success': False, 'error': str(e)})

# Add this route to your Flask app
    """
    This function is a route in a Flask app that allows the user to select a contact to edit and
    redirects them to the edit page for that contact.
    :return: the rendered template "select_contact_to_edit.html" with the contacts passed as a
    parameter.
    """
@app.route("/select_contact_to_edit", methods=["GET", "POST"])
@login_required
def select_contact_to_edit():
    selected_language = select_language()
    if request.method == "POST":
        # Retrieve the selected contact ID from the form
        selected_contact_id = int(request.form.get("contact_id"))
        # Redirect to the edit page for the selected contact
        return redirect(url_for("edit", contact_id=selected_contact_id))

    # Query all contacts to display in the selection form
    contacts = Contact.query.all()
    return render_template(
        f"{selected_language}/select_contact_to_edit.html", contacts=contacts
    )


# delete route
    """
    The `select_contact_to_delete` function is a route in a Flask application that allows the user to
    select a contact to delete and redirects them to the delete page for that contact.
    :return: the rendered template "select_contact_to_delete.html" with the contacts passed as a
    parameter.
    """
@app.route("/select_contact_to_delete", methods=["GET", "POST"])
@login_required
def select_contact_to_delete():
    selected_language = select_language()
    if request.method == "POST":
        # Retrieve the selected contact ID from the form
        selected_contact_id = int(request.form.get("contact_id"))
        # Redirect to the edit page for the selected contact
        return redirect(url_for("delete", contact_id=selected_contact_id))

    # Query all contacts to display in the selection form
    contacts = Contact.query.all()
    return render_template(
        f"{selected_language}/select_contact_to_delete.html", contacts=contacts
    )


# langauge select route
    """
    The `change_language` function changes the current language setting of the app to either "chinese"
    or "english" and redirects the user back to the previous page.
    :return: a redirect to the previous page (request.referrer).
    """
@app.route("/change_language")
def change_language():
    current_language = app.config["select_language"]
    new_language = "chinese" if current_language == "english" else "english"
    app.config["select_language"] = new_language
    return redirect(request.referrer)


# get current language
    """
    The above function returns the current language selected in the application.
    :return: The current language selected by the user.
    """
@app.route("/get_language")
def get_language():
    return app.config["select_language"]


# login route
    """
    The `login` function is a route in a Python Flask application that handles user login functionality,
    including checking the username and password against a SQLite database and storing the username in a
    session if the login is successful.
    :return: the rendered template for the login page.
    """
@app.route("/login", methods=["GET", "POST"])
def login():
    selected_language = select_language()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect("login.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password),
            )
            result = cursor.fetchone()
        if result:
            session["username"] = username
            flash("You have successfully logged in.")
            return redirect(url_for("index"))
        else:
            flash("login failed. try again")

    return render_template(f"{selected_language}/login.html")


# logout route
    """
    The above function is a logout route that removes the "username" key from the session, displays a
    flash message, and redirects the user to the login page.
    :return: a redirect to the "login" route.
    """
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have successfully logged out.")
    return redirect(url_for("login"))


# register route
    """
    The `register` function handles the registration process, including checking the secret password,
    inserting the user into the database, and displaying the registration form.
    :return: the rendered template for the register page.
    """
@app.route("/register", methods=["GET", "POST"])
def register():
    selected_language = select_language()
    if request.method == "POST":
        # check if secret password is correct
        secret_password = request.form.get("secret_password")
        if secret_password != SECRET_PASSWORD:
            flash(
                "You are not authorized to register, Please contact system admin. 您沒有權限註冊，請聯絡系統管理員。"
            )
            return redirect(url_for("register"))

        # if secret password is correct, continue with registration
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect("login.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            connection.commit()
        flash("Registation successful.")
        return redirect(url_for("login"))

    return render_template(f"{selected_language}/register.html")

# Route for deleting a contact
    """
    This function deletes a contact from the database based on the provided contact_id.
    
    :param contact_id: The contact_id parameter is the unique identifier of the contact that needs to be
    deleted. It is passed as a parameter in the URL route
    :return: The route is returning a JSON response with a message indicating that the contact has been
    deleted successfully.
    """
@app.route('/delete_contact/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'Contact deleted successfully'})

@app.route('/delete_selected_contacts_js', methods=['DELETE'])
@login_required
def delete_selected_contacts_js():
    data = request.get_json()
    selected_contact_ids = data.get('selected_contact_ids', [])

    for contact_id in selected_contact_ids:
        contact = Contact.query.get(contact_id)
        if contact:
            db.session.delete(contact)

    db.session.commit()
    return jsonify({'message': 'Selected contacts deleted successfully'})


@app.route('/generate_csv', methods=['POST'])
def generate_csv():
    # Your logic to get selected contact IDs
    selected_contact_ids = request.json.get('selected_contact_ids', [])

    # Fetch contacts based on selected IDs
    selected_contacts = Contact.query.filter(Contact.id.in_(selected_contact_ids)).all()

    # Create a CSV string
    csv_content = generate_csv_content(selected_contacts)

    return jsonify({'csv_content': csv_content})

def generate_csv_content(contacts):
    # Use StringIO to create an in-memory file-like object
    csv_output = StringIO()
    
    # Create a CSV writer
    csv_writer = csv.writer(csv_output)

    # Write header
    csv_writer.writerow(['Tag', 'First Name', 'Last Name', 'Company', 'Department', 'Job Title', 'E-mail Address', 'E-mail Address 2', ' Business Phone', 'Mobile Phone', 'Business Fax', 'Birthday', 'Business Address', 'Business City', 'Business State', 'Business Zip', 'Business Country', 'Web Page','Notes' ])  # Add more fields as needed

    # Write data for all headers
    for contact in contacts:
        csv_writer.writerow([contact.tag, contact.first_name, contact.last_name, contact.company, contact.department, contact.job_title, contact.email_address, contact.email_address_2, contact.business_phone, contact.mobile_phone, contact.business_fax, contact.birthday, contact.business_address, contact.business_city, contact.business_state, contact.business_zip, contact.business_country, contact.web_page, contact.notes])  # Add all header fields here

    # Get the CSV content as a string
    csv_content = csv_output.getvalue()

    # Close the StringIO buffer
    csv_output.close()

    return csv_content

# The above code is running a Flask app. It first initializes the database by calling the `init_db()`
# function. Then, it creates all the necessary database tables using the `db.create_all()` method
# within a Flask application context. Finally, it runs the Flask app with debugging enabled
# (`debug=True`), allowing for error messages to be displayed, and sets the host to "0.0.0.0" and the
# port to 5000.
# Run the Flask app
if __name__ == "__main__":
    init_db()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
