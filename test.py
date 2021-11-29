@app.route("/user_activity_history/<username>", methods=["GET", "POST"])
def user_activity_history(username):

    activities = list(mongo.db.activities.find({"username": session["user"],"completed":"yes"}).sort("target_date", 1))

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    return render_template("user_activity_history.html", username=username, activities=activities)


