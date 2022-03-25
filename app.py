from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'W8wfyR2ERM'
app.config['SESSION_TYPE'] = 'filesystem'

client  = MongoClient('localhost',27017)
db = client.db1


# just for testing purpose
@app.route('/hello')
def hello_world():
    return "Hello world!"


# just for testing purpose
@app.route('/login')
def redirect_login():
    return redirect(url_for(".login"))



@app.route('/profile')
def profile():
    if session['username']:
        username = session['username']
        return render_template("profile.html",username=username)
    else:
        return redirect(url_for('.login'))  


# render login form
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.users.find_one({"username":username,"password":password})
        if user:
            session['username'] = user.get('username')
            return redirect(url_for('.profile')) 
        else:
            return redirect('/')   
    else:
        if session['username']:
            return redirect(url_for('.profile'))
        else:
            return render_template("login.html")


# render login form
@app.route("/register", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.users.find_one({"username":username,"password":password})
        if user:
            session['username'] = user.get('username')
            return redirect(url_for('.profile')) 
        else:
            return redirect('/')   
    else:
        if session['username']:
            return redirect(url_for('.profile'))
        else:
            return render_template("signup.html")



# handle logout
@app.route("/logout", methods=["POST"])
def logout():
    session['username'] = None
    return redirect('/');  


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)