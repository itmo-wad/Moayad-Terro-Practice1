import os
from flask import Flask, flash, render_template, request, session, redirect, url_for, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)
# session and uploaded folder
app.secret_key = 'W8wfyR2ERM'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = './upload'

# for db and connection
client  = MongoClient('localhost',27017)
db = client.db1

# for image type uploaded
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# just for testing purpose
@app.route('/hello')
def hello_world():
    return "Hello world!"


# render home
@app.route('/')
def home():
    return render_template("index.html")



@app.route('/auth')
def profile():
    if session['username']:
        username = session['username']
        return render_template("profile.html",username=username)
    else:
        return redirect(url_for('.login'))  


# render login form
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.users.find_one({"username":username})
        if user and check_password_hash(user.get('password'),password):
            session['username'] = user.get('username')
            return redirect(url_for('.profile')) 
        else:   
            flash('Username or password incorrect!')
            return redirect(request.url)
    else:
        if session.get('username'):
            return redirect(url_for('.profile'))
        else:
            return render_template("login.html")


# render login form
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "")
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.users.find_one({"username":username})
        if user:
            flash('Username already exist!')
            return redirect(request.url)
        else:
            # here write  sign up logic
            db.users.insert_one({
                "name":name,
                "username":username,
                "password":generate_password_hash(password)
            })
            flash('Account created! Please login')
            return redirect(url_for(".login"))   
    else:
        if session.get('username'):
            return redirect(url_for('.profile'))
        else:
            return render_template("signup.html")



# handle logout
@app.route("/logout", methods=["POST"])
def logout():
    session['username'] = None
    return redirect('/');  



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if not allowed_file(file.filename):
            flash('Invalid file extension', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            flash('Successfully saved', 'success')
            return redirect(url_for('uploaded_file', filename=filename))
        
            
    return render_template("upload.html")




@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/notebook', methods=['GET', 'POST','DELETE'])
def notebook():
    if request.method == 'POST':
        note = request.form.get("note", "")
        db.notes.insert_one({
            "note":note,
        })
        flash('note added successfully!')
        return redirect(request.url)

    elif request.method =="DELETE":
        flash('note deleted successfully!')
        return redirect(request.url)
    perPage =int(request.args.get("perPage", "10"))
    notes = db.notes.find().limit (perPage)
    print(notes)
    return render_template('notebook.html',data=notes)


@app.route('/notebook/delete', methods=['POST'])
def notebook_delete():
    db.notes.delete_many({})
    flash('note deleted successfully!')
    return redirect(url_for(".notebook"))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)