from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Student, Teacher, Course, User
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    return("PRIVET")

@app.route("/courses")
def courses():
    courses = Course.query.all()
    return render_template("courses.html", courses=courses)


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
    app.run(debug=True)
