from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask_login import UserMixin
from sqlalchemy import JSON

db = SQLAlchemy()

enrollments = db.Table(
    "enrollments",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)

    courses = db.relationship(
        "Course", secondary=enrollments, back_populates="students"
    )

    def __repr__(self):
        return f"student {self.name}"


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)

    courses = db.relationship("Course", backref="teacher")


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))

    students = db.relationship(
        "Student", secondary=enrollments, back_populates="courses"
    )

    def __repr__(self):
        return f"course {self.title}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="student")
    permissions = db.Column(JSON, default={})

    def __repr__(self):
        return f"user {self.username}"

    def has_permission(self, resource, action):
        return action in self.permissions.get(resource, [])
    
    