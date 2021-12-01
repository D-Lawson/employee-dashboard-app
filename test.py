@app.route("/user_activity_history/<username>", methods=["GET", "POST"])
def user_activity_history(username):

    activities = list(mongo.db.activities.find({"username": session["user"],"completed":"yes"}).sort("target_date", 1))

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    return render_template("user_activity_history.html", username=username, activities=activities)



def home():
    if session["user"] == "admin":
        return redirect(url_for("admin_dashboard"))
    elif session["user"] != "admin":
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))




