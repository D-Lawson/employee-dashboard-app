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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        current_username = request.form.get("username").lower()

        if check_user and current_username == "admin":
            if check_password_hash(
                    check_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Hello {}, you are signed in to your Admin dashboard".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "admin_dashboard", username=session["user"]))
        elif check_user and current_username != "admin":
            if check_password_hash(
                    check_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        return redirect(url_for(
                            "dashboard", username=session["user"]))
            else:
                flash("The Password and/or Username is incorrect.  Please try again.")
                return redirect(url_for("login"))

        else:
            flash("The Password and/or Username is incorrect.  Please try again.")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        check_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if check_user:
            flash("This username is already registered")
            return redirect(url_for("register"))

        create_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(create_user)

        session["user"] = request.form.get("username").lower()
        flash("Thank you for registering.  Your are now signed in to your personal dashboard.")
        return redirect(url_for("dashboard", username=session["user"]))

    return render_template("register.html")


@app.route("/logout")
def logout():
    flash("Sucessfully logged out from dashboard")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/dashboard/<username>", methods=["GET", "POST"])
def dashboard(username):

    activities = list(mongo.db.activities.find({"username": session["user"]}))

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("dashboard.html", activities=activities, username=username)

    return redirect(url_for("login"))


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
    
    activities = list(mongo.db.activities.find({"completed":"no"}).sort("target_date", 1))


    users = mongo.db.users.find().sort("username", 1)
    return render_template("admin_dashboard.html", users=users, activities=activities)


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


@app.route("/delete_activity/<activity_id>")
def delete_activity(activity_id):
    mongo.db.activities.remove({"_id": ObjectId(activity_id)})
    flash("Activity Deleted")
    return redirect(url_for("admin_dashboard"))


@app.route("/completed/<activity_id>")
def completed(activity_id):

    completed = {
        "completed": "yes",
    }

    mongo.db.activities.update_one({"_id": ObjectId(activity_id)},{"$set":completed})

    flash("Activity marked as complete")
    return redirect(url_for("admin_dashboard"))


@app.route("/activity_history", methods=["GET", "POST"])
def activity_history():
    
    activities = list(mongo.db.activities.find({"completed":"yes"}).sort("target_date", 1))

    users = mongo.db.users.find().sort("username", 1)
    return render_template("activity_history.html", users=users, activities=activities)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
