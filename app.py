from flask import Flask, render_template, request, redirect, url_for, make_response, session
from config import Config
from models import db, Student, Teacher, Course, User, ShortLink, text
from datetime import timedelta
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
from markupsafe import escape
from flask_socketio import SocketIO, send
from tasks import long_task


app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(minutes=1)
db.init_app(app)
socketio = SocketIO(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/start_background_task", methods=["POST"])
def start_background_task():
    email=request.form.get("email")
    long_task.delay(email)
    return "task started in background"


@app.route("/background_work")
def background_work():
    return render_template("backround_task.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # query = text("SELECT * FROM user WHERE username =:username AND password =:password")
        # hacker_result=db.session.execute(query,{"username":username,"password":password}).fetchone()
        # return f"you hacked {hacker_result}"
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/admin_page", methods=["GET", "POST"])
@login_required
def admin_page():
    users = User.query.all()
    if request.method == "POST":
        user_id = request.form.get("user_id")
        permissions = request.form.getlist("permissions")
        user = User.query.get(user_id)

        if not user:
            return "user not found", 404
        new_permissions = {}
        for perm in permissions:
            print(perm)
            resource, action = perm.split(":")
            if resource not in new_permissions:
                new_permissions[resource] = []
            new_permissions[resource].append(action)
        user.permissions = new_permissions
        db.session.commit()

        return redirect(url_for("admin_page"))

    return render_template("admin_users.html", users=users,all_permissions=app.config["ALL_PERMISSIONS"])



@app.route("/")
@login_required
def home():
    students = Student.query.all()
    return render_template("index.html", students=students, current_user=current_user)


@app.route("/teachers")
def teachers():
    if not current_user.has_permission("teachers_page", "read"):
        return "Access denied", 403

    teachers = Teacher.query.all()
    return render_template(
        "teachers.html", teachers=teachers, current_user=current_user
    )

@app.route("/test")
def test():
    return("PAKA")

@app.route("/courses")
def courses():
    courses = Course.query.all()
    return render_template("courses.html", courses=courses)

@app.route("/set_custom_cookie")
def set_custom_cookie():
    username=request.args.get("username","guest")
    response = make_response(f"my name is {username}")
    response.set_cookie("username",username )
    return response

@app.route("/get_custom_cookie")
def get_cookie():
    username= request.cookies.get("username")
    return f"hello {username}, welcome here"

@app.route("/set_custom_session")
def set_custom_session():
    session.permanent = True
    session["my_session"] = 12345
    return "session saved"

@app.route("/get_custom_session")
def get_custom_session():
    return f"result:{session["my_session"]}"


def generate_short_link():
    symbols=string.ascii_letters+string.digits
    six_random_symbols=""
    for i in range(6):
        six_random_symbols += random.choice(symbols)
    return six_random_symbols

@app.route("/short_link",methods=["POST"])
def short_link():
    long_url=request.form["url"]
    shorter_link = generate_short_link()
    result=ShortLink(short_link=shorter_link,link=long_url)
    db.create_all()
    db.session.add(result)
    db.session.commit()
    return f"short url is -> {shorter_link}"

@app.route("/<shortcode>")
def redirect_url(shortcode):
    target_url = ShortLink.query.filter_by(short_link=shortcode).first()
    if target_url:
        return redirect(target_url.link)
    return("not found")

@app.route("/testik")
def testik():
    return """
    <h2>URL Shortener</h2>
    <form method="POST" action="/short_link">
        <input name="url" placeholder="Enter URL" style="width:300px"/>
        <button type="submit">Shorten</button>
    </form>
    """

@app.route("/bad_profile")
def bad_profile():
    username = request.args.get("name")
    return f"<h1>Hello {username}</h1>"

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/return_json")
def return_json():
    return{"strogo":0.5, "bmw":5}

@app.route("/custom_login_page")
def custom_login_page():
    return """
    <h1>
    custom login page
    </h1>
    <form method="POST" action="/custom_login">
        <input name="username" placeholder="please enter your username"><br>
        <input name="password" placeholder="please enter your password" type="password"><br>
        <button type="submit">login</button>

    </form>

    """

@app.route("/custom_login", methods=["POST"])
def custom_login():
    username=request.form.get("username")
    password=request.form.get("password")
    if username=="dog" and password=="cat":
        return"succesfully login"
    else: 
        return "invalid username or password"


@socketio.on("message")
def handle_message(msg):
    print(f"message:{msg}")
    send(msg, broadcast=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not Teacher.query.first():
            teacher = User(
                username="valeriy",
                password=generate_password_hash("1234"),
                role="teacher",
            )
            user = User(
                username="Kosty",
                password=generate_password_hash("1234"),
                role="teacher",
                permissions={"teachers_page": ["read", "create", "update"]},
            )

            teacher_one = Teacher(name="Biba", surname="Boba")
            teacher_two = Teacher(name="Serega", surname="Petrovich")

            course_one = Course(title="Matematika", teacher=teacher_one)
            course_two = Course(title="Ukrainska Mova", teacher=teacher_two)

            student_one = Student(name="Nikitos", surname="Staroselskyi")
            student_two = Student(name="Deniska", surname="Reznikov")

            student_one.courses.append(course_one)
            student_one.courses.append(course_two)
            student_two.courses.append(course_two)
            student_two.courses.append(course_one)

            db.session.add_all(
                [
                    user,
                    teacher,
                    teacher_one,
                    teacher_two,
                    course_one,
                    course_two,
                    student_one,
                    student_two,
                ]
            )
            db.session.commit()
    socketio.run(app, debug=True)

