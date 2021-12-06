import os
from datetime import datetime
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
# User login authentication.
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticates user and validates the hashed password
    """
    redirect_to_dashboard_if_authenticated()

    if request.method == "POST":
        current_username = request.form.get("username").lower()
        check_user = mongo.db.users.find_one(
            {"username": current_username})
        current_password = request.form.get("password")

        if check_user and current_username == "admin":
            if check_password_hash(
                    check_user["password"], current_password):
                session["user"] = current_username
                return redirect(url_for("admin_dashboard"))
            else:
                flash("The Password and/or Username is incorrect.")
                return redirect(url_for("login"))
        elif check_user and current_username != "admin":
            if check_password_hash(
                    check_user["password"], current_password):
                session["user"] = current_username
                return redirect(url_for("dashboard"))
            else:
                flash("The Password and/or Username is incorrect.")
                return redirect(url_for("login"))
        else:
            flash("The Password and/or Username is incorrect.")
            return redirect(url_for("login"))
    return render_template("login.html")


# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers new user into db and generates hashed p/w
    """
    redirect_to_dashboard_if_authenticated()

    if request.method == "POST":
        current_user = request.form.get("username").lower()
        check_user = mongo.db.users.find_one(
            {"username": current_user})

        if check_user:
            flash("This username is already registered")
            return redirect(url_for("register"))

        create_user = {
            "username": current_user,
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(create_user)

        session["user"] = current_user
        flash(
            """Thank you for registering.  You are now signed in
            to your personal dashboard.""")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


# User log out
@app.route("/logout")
def logout():
    """
    Logs the user out of the system
    """
    if is_authenticated():
        flash("Sucessfully logged out from dashboard")
        session.pop("user")

    return redirect(url_for("login"))


# User dashboard
@app.route("/dashboard/", methods=["GET", "POST"])
def dashboard():
    """
    Renders the user's dashboard, retrieves/sorts all uncompleted activities
    """
    if not is_authenticated():
        return redirect(url_for("login"))

    current_user = session["user"]

    activities = list(mongo.db.activities.find(
        {"username": current_user, "completed": "no"}).sort("target_date", 1))

    username = mongo.db.users.find_one(
        {"username": current_user})["username"]

    if current_user:
        return render_template(
            "dashboard.html", activities=activities, username=username)

    return redirect(url_for("login"))


# Admin dashboard
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    """
    Renders the admin dashboard including all uncompleted activities
    """

    if not is_admin_authenticated():
        return redirect(url_for("login"))

    if request.method == "POST":
        datestring = request.form.get("target_date")
        unixdate = datetime.strptime(datestring, "%d %B, %Y").date()
        unixtime = datetime.now().time()
        combine = datetime.combine(unixdate, unixtime)
        print(combine)
        activity = {
            "username": request.form.get("assign_to"),
            "activity_name": request.form.get("activity_name"),
            "activity_description": request.form.get("activity_description"),
            "target_date": combine,
            "date_string": datestring,
            "completed": "no",
        }
        mongo.db.activities.insert_one(activity)
        flash("Activity successfully assigned to user")
        return redirect(url_for("admin_dashboard"))

    activities = list(mongo.db.activities.find(
        {"completed": "no"}).sort("target_date", 1))

    users = mongo.db.users.find().sort("username", 1)
    return render_template(
        "admin_dashboard.html", users=users, activities=activities)


# Edit activity
@app.route("/edit_activity/<activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):
    """
    Edits the selected activity ID and updates db
    """

    if not is_admin_authenticated():
        return redirect(url_for("login"))

    if request.method == "POST":
        datestring = request.form.get("target_date")
        unixdate = datetime.strptime(datestring, "%d %B, %Y").date()
        unixtime = datetime.now().time()
        combine = datetime.combine(unixdate, unixtime)
        print(combine)
        update = {
            "username": request.form.get("assign_to"),
            "activity_name": request.form.get("activity_name"),
            "activity_description": request.form.get("activity_description"),
            "target_date": combine,
            "date_string": datestring,
            "completed": "no",
        }
        mongo.db.activities.update({"_id": ObjectId(activity_id)}, update)
        flash("Activity successfully updated")
        return redirect(url_for("admin_dashboard"))
    activity = mongo.db.activities.find_one({"_id": ObjectId(activity_id)})
    users = mongo.db.users.find().sort("username", 1)

    return render_template(
        "edit_activity.html", activity=activity, users=users)


# Delete activity
@app.route("/delete_activity/<activity_id>")
def delete_activity(activity_id):
    """
    Deletes the selected activity ID from db.
    """
    if not is_admin_authenticated():
        return redirect(url_for("login"))

    mongo.db.activities.remove({"_id": ObjectId(activity_id)})
    flash("Activity Deleted")
    return redirect(url_for("admin_dashboard"))


#  Mark activity as completed
@app.route("/completed/<activity_id>")
def completed(activity_id):
    """
    Marks the selected activity ID as completed in db
    """
    if not is_authenticated():
        return redirect(url_for("login"))

    current_user = session["user"]

    completed_activity = {"completed": "yes"}

    unixdate = datetime.now().date()
    unixtime = datetime.now().time()
    combine = datetime.combine(unixdate, unixtime)

    mongo.db.activities.update_one(
        {"_id": ObjectId(activity_id)}, {"$set": completed_activity})

    mongo.db.activities.update_one(
        {"_id": ObjectId(activity_id)}, {"$set": {"date_completed": combine}})

    flash("Activity marked as complete")

    if current_user != "admin":
        return redirect(url_for("dashboard", username=current_user))

    return redirect(url_for("admin_dashboard"))


# Render all activity history
@app.route("/activity_history")
def activity_history():
    """
    Renders all completed activities with sort and filter
    """
    if is_admin_authenticated():
        activities = list(mongo.db.activities.find(
            {"completed": "yes"}).sort("target_date", 1))
        users = mongo.db.users.find().sort("username", 1)
        return render_template(
            "activity_history.html", users=users, activities=activities)

    return redirect(url_for("login"))


# Render user specific activity
@app.route("/user_activity_history", methods=["GET", "POST"])
def user_activity_history():
    """
    Renders all completed activities for the active user
    """
    if not is_authenticated():
        return redirect(url_for("login"))

    current_user = session["user"]
    activities = list(mongo.db.activities.find(
        {"username": current_user, "completed": "yes"}).sort(
            "target_date", 1))

    return render_template(
        "user_activity_history.html",
        activities=activities, username=current_user)


# Other functions
def is_authenticated():
    """
    Checks the active user
    """
    return 'user' in session


def is_admin_authenticated():
    """
    Checks whether the active user is the admin
    """
    return is_authenticated() and session['user'] == "admin"


def redirect_to_dashboard_if_authenticated():
    """
    Redirects to user or admin dashboard if authenticated
    """
    if is_admin_authenticated():
        return redirect(url_for("admin_dashboard"))
    elif is_authenticated():
        return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
