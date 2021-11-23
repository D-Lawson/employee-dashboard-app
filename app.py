import os
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if check_user:
            if check_password_hash(
                    check_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Hello {}, you are signed in to your personal dashboard".format(
                            request.form.get("username")))
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

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
