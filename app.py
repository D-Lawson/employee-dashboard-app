import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")


# User login authentication.  Validate hashed password.
@app.route("/login", methods=["GET", "POST"])
def login():

    if is_admin_authenticated():
        return redirect(url_for("admin_dashboard"))
    elif check_authentication():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        check_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        current_username = request.form.get("username").lower()
        current_password = request.form.get("password")

        if check_user and current_username == "admin":
            if check_password_hash(
                    check_user["password"], current_password):
                session["user"] = current_username
                return redirect(url_for("admin_dashboard"))
        elif check_user and current_username != "admin":
            if check_password_hash(
                    check_user["password"], current_password):
                session["user"] = current_username
                return redirect(url_for("dashboard"))
            else:
                flash("The Password and/or Username is incorrect.  Please try again.")
                return redirect(url_for("login"))

        else:
            flash("The Password and/or Username is incorrect.  Please try again.")
            return redirect(url_for("login"))
    return render_template("login.html")


# User registration with hashed password generator
@app.route("/register", methods=["GET", "POST"])
def register():
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
            "Thank you for registering.  Your are now signed in to your personal dashboard.")
        return redirect(url_for("dashboard"))

    return render_template("register.html")

# User log out
@app.route("/logout")
def logout():
    flash("Sucessfully logged out from dashboard")
    session.pop("user")
    return redirect(url_for("login"))


# User dashboard, retrieve and sort data from db
@app.route("/dashboard/", methods=["GET", "POST"])
def dashboard():

    current_user = session["user"]

    activities = list(mongo.db.activities.find(
        {"username": current_user, "completed": "no"}).sort("target_date", 1))

    username = mongo.db.users.find_one(
        {"username": current_user})["username"]

    if current_user:
        return render_template("dashboard.html", activities=activities, username=username)

    return redirect(url_for("login"))


# Admin dashboard, retrieve and sort data from db
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
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
    return render_template("admin_dashboard.html", users=users, activities=activities)


# Edit activity and update db
@app.route("/edit_activity/<activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):
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

    return render_template("edit_activity.html", activity=activity, users=users)


# Delete activity
@app.route("/delete_activity/<activity_id>")
def delete_activity(activity_id):
    mongo.db.activities.remove({"_id": ObjectId(activity_id)})
    flash("Activity Deleted")
    return redirect(url_for("admin_dashboard"))


#  Mark activity as completed
@app.route("/completed/<activity_id>")
def completed(activity_id):

    current_user = session["user"]

    completed = {
        "completed": "yes",
    }

    mongo.db.activities.update_one(
        {"_id": ObjectId(activity_id)}, {"$set": completed})

    flash("Activity marked as complete")

    if current_user != "admin":
        return redirect(url_for("dashboard", username=current_user))

    return redirect(url_for("admin_dashboard"))


# Render all activity history from db with sort and filter
@app.route("/activity_history")
def activity_history():

    if is_admin_authenticated():
        activities = list(mongo.db.activities.find(
            {"completed": "yes"}).sort("target_date", 1))
        users = mongo.db.users.find().sort("username", 1)
        return render_template("activity_history.html", users=users, activities=activities)

    return redirect(url_for("login"))


# Render user specific activity history from db with sort and filter
@app.route("/user_activity_history", methods=["GET", "POST"])
def user_activity_history():

    current_user = session["user"]

    if not is_admin_authenticated():
        activities = list(mongo.db.activities.find(
            {"username": current_user, "completed": "yes"}).sort("target_date", 1))
        username = mongo.db.users.find_one(
            {"username": current_user})["username"]
    if current_user:
        return render_template("user_activity_history.html", activities=activities, username=username)

    return redirect(url_for("login"))


# Check active user for authentication
def check_authentication():
    return 'user' in session


# Check if active user is the admin
def is_admin_authenticated():
    return check_authentication() and session['user'] == "admin"



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
