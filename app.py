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
    login_required,
    admin_required,
    check_csv_encoding,
    detect_and_convert_encoding,
    init_user_db,
)
from modules.contacts import Contact, db
from io import TextIOWrapper, BytesIO, StringIO
import csv
import sqlite3

# The above code is initializing a Flask app and configuring the database connection.
# Initialize the Flask app
app = Flask(__name__, static_folder="static", static_url_path="")


# Configure the database connection
app.secret_key = "3LKENMg6RtmEqC9gFY83xsSDMFQffpDYkHnyyCms"
SECRET_PASSWORD = "VIRTUIT"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["select_language"] = "english"
db.init_app(app)


def select_language():
    return app.config["select_language"]

# Homepage route to display the database
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


# Upload route for handling CSV file upload
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
                if session[""] == 1:
                    flash("File uploaded successfully", "success")
                    return redirect("/_index")
                else:
                    flash("File uploaded successfully", "success")
                return redirect("/")
            else:
                flash("Invalid file format. Please upload a CSV file.", "danger")

        except Exception as e:
            flash(f"Error uploading file: {str(e)}", "danger")

    return render_template(f"{selected_language}/upload.html")

# Upload route for handling CSV file upload
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

    if session[""] == 1:
        flash("File uploaded successfully", "success")
        return redirect("/_index")
    else:
        flash("File uploaded successfully", "success")
    return redirect("/")

    return render_template(f"{selected_language}/upload.html")


# Search route for searching the database
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
        ).all()
        return render_template(
            f"{selected_language}/search_results.html", contacts=contacts, query=query
        )
    return render_template(f"{selected_language}/search.html")


# Search only email results
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
        ).all()
        return render_template(
            f"{selected_language}/search_email_results.html",
            contacts=contacts,
            query=query,
        )
    return render_template(f"{selected_language}/search_email.html")

# edit contact
@app.route("/edit/<int:contact_id>", methods=["GET", "POST"])
@login_required
@admin_required
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
        if session.get("") == 1:
            flash("Contact updated successfully", "success")
            return redirect("/_index")
        else:
            flash("Contact updated successfully", "success")
            return redirect("/")
    
    return render_template(
        f"{selected_language}/edit.html", contact=contact, headers=headers
    )


# delete contact
@app.route("/delete/<int:contact_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete(contact_id):
    selected_language = select_language()
    contact = Contact.query.get_or_404(contact_id)

    if request.method == "POST":
        # Delete the contact and redirect to the home page
        db.session.delete(contact)
        db.session.commit()
        if session.get("") == 1:
            flash("Contact deleted successfully", "success")
            return redirect("/_index")
        else:
            flash("Contact deleted successfully", "success")
            return redirect("/")

    return render_template(f"{selected_language}/delete.html", contact=contact)


# Route for deleting selected contacts
@app.route('/delete_selected', methods=['POST'])
@login_required
@admin_required
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

        if session.get("") == 1:
            flash('Contacts deleted successfully', 'success')
            return redirect("/_index")
        else:
            return jsonify({'success': True, 'message': 'Contacts deleted successfully'})
    except Exception as e:
        print(f"Error deleting:{str(e)}")
        if session.get("") == 1:
            flash('Error deleting contacts', 'error')
            return redirect("/_index")
        else:
            return jsonify({'message':'Error deleting contacts', 'success': False, 'error': str(e)})

# Route for selecting a contact to edit
@app.route("/select_contact_to_edit", methods=["GET", "POST"])
@login_required
@admin_required
def select_contact_to_edit():
    selected_language = select_language()
    if request.method == "POST":
        # Retrieve the selected contact ID from the form
        selected_contact_id = int(request.form.get("contact_id"))
        # Redirect to the edit page for the selected contact
        if session.get("") == 1:
            flash('Contact selected successfully for editing', 'success')
            return redirect(url_for("edit", contact_id=selected_contact_id))
        else:
            flash('You do not have permission to edit contacts', 'error')
            return redirect("/")

    # Query all contacts to display in the selection form
    contacts = Contact.query.all()
    return render_template(
        f"{selected_language}/select_contact_to_edit.html", contacts=contacts
    )


# Route for selecting a contact to delete
@app.route("/select_contact_to_delete", methods=["GET", "POST"])
@login_required
@admin_required
def select_contact_to_delete():
    selected_language = select_language()
    if request.method == "POST":
        # Retrieve the selected contact ID from the form
        selected_contact_id = int(request.form.get("contact_id"))
        # Redirect to the delete page for the selected contact
        if session.get("") == 1:
            flash('Contact selected successfully for deletion', 'success')
            return redirect(url_for("delete", contact_id=selected_contact_id))
        else:
            flash('You do not have permission to delete contacts', 'error')
            return redirect("/")

    # Query all contacts to display in the selection form
    contacts = Contact.query.all()
    return render_template(
        f"{selected_language}/select_contact_to_delete.html", contacts=contacts
    )


# langauge select route
@app.route("/change_language")
def change_language():
    current_language = app.config["select_language"]
    new_language = "chinese" if current_language == "english" else "english"
    app.config["select_language"] = new_language
    return redirect(request.referrer)


# get current language
@app.route("/get_language")
def get_language():
    return app.config["select_language"]


# login route
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
            session["username"] = result[1]
            session["role"] = result[3]
            flash("You have successfully logged in.")
            return redirect(url_for("index"))
        else:
            flash("login failed. try again")

    return render_template(f"{selected_language}/login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have successfully logged out.")
    return redirect(url_for("login"))


# register route
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
        admin = request.form.get("admin")

        with sqlite3.connect("login.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, admin),
            )
            connection.commit()
        flash("Registation successful.")
        return redirect(url_for("login"))

    return render_template(f"{selected_language}/register.html")


# Route for deleting a contact
@app.route('/delete_contact/<int:contact_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'Contact deleted successfully'})

@app.route('/delete_selected_contacts_js', methods=['DELETE'])
@login_required
@admin_required
def delete_selected_contacts_js():
    data = request.get_json()
    selected_contact_ids = data.get('selected_contact_ids', [])

    for contact_id in selected_contact_ids:
        contact = Contact.query.get(contact_id)
        if contact:
            db.session.delete(contact)

    db.session.commit()
    render_template('index.html')
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
    init_user_db()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
