from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    session,
    flash,
)
from modules.functions import (
    csv_to_db_mapping,
    csv_to_db_mapping_zh,
    load_csv_to_db,
    load_csv,
    init_db,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, _
from modules.contacts import Contact, db
from io import TextIOWrapper, BytesIO
import csv
import sqlite3

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
    """_summary_

    Returns:
        _type_: _description_
    """


# Upload route for handling CSV file upload
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
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
@app.route("/upload_convert_csv", methods=["GET", "POST"])
@login_required
def upload_convert_csv():
    selected_language = select_language()
    if request.method == "POST":
        uploaded_file = request.files["csvFileSecond"]
        utf8_content = load_csv(uploaded_file)

        # Use BytesIO to create a downloadable file
        download_file = BytesIO()
        download_file.write(utf8_content.getvalue())
        download_file.seek(0)

        # Provide the file for download
        return send_file(
            download_file,
            mimetype="text/csv",
            as_attachment=True,
            download_name="converted_file.csv",
        )
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
        "Other Phone": "other_phone",
        "Primary Phone": "primary_phone",
        "Business Fax": "business_fax",
        "Job Title": "job_title",
        "Company": "company",
        "Business Address": "business_address",
        "Business City": "business_city",
        "Business State": "business_state",
        "Business Postal Code": "business_zip",
        "Business Country/Region": "business_country",
        "Personal Web Page": "personal_website",
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
        "Other Phone": "other_phone",
        "Primary Phone": "primary_phone",
        "Business Fax": "business_fax",
        "Job Title": "job_title",
        "Company": "company",
        "Business Address": "business_address",
        "Business City": "business_city",
        "Business State": "business_state",
        "Business Postal Code": "business_zip",
        "Business Country/Region": "business_country",
        "Personal Web Page": "personal_website",
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


# Add this route to your Flask app
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
            session["username"] = username
            flash("You have successfully logged in.")
            return redirect(url_for("index"))
        else:
            flash("login failed. try again")

    return render_template(f"{selected_language}/login.html")


# logout route
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


# Run the Flask app
if __name__ == "__main__":
    init_db()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
