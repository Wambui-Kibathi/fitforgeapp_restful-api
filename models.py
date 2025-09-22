from app import db, bcrypt
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
import re

# User model
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    workouts = db.relationship("Workout", back_populates="user", cascade="all, delete-orphan")

    serialize_rules = ("-workouts.user", "-password_hash")

    # Password handling
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Validations
    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return username.strip()

    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        return email.strip()

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


# Workout model
class Workout(db.Model, SerializerMixin):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Relationships
    user = db.relationship("User", back_populates="workouts")
    workout_exercises = db.relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")

    serialize_rules = ("-user.workouts", "-workout_exercises.workout")

    # Validations
    @validates('type')
    def validate_type(self, key, workout_type):
        if not workout_type or len(workout_type.strip()) < 2:
            raise ValueError("Workout type must be at least 2 characters long")
        return workout_type.strip()

    @validates('duration')
    def validate_duration(self, key, duration):
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if duration > 360:
            raise ValueError("Duration too long (max 360 minutes)")
        return duration

    @validates('calories_burned')
    def validate_calories(self, key, calories):
        if calories is not None and calories < 0:
            raise ValueError("Calories burned cannot be negative")
        return calories

    def __repr__(self):
        return f"<Workout {self.type} ({self.duration} min)>"

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'notes': self.notes,
            'date': self.date.isoformat() if self.date else None,
            'user_id': self.user_id,
            'exercises': [we.to_dict() for we in self.workout_exercises]
        }


# Exercise model (for many-to-many relationship)
class Exercise(db.Model, SerializerMixin):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50))  # e.g., "Cardio", "Strength", "Flexibility"

    # Relationships
    workout_exercises = db.relationship("WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan")

    serialize_rules = ("-workout_exercises.exercise",)

    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters long")
        return name.strip()

    def __repr__(self):
        return f"<Exercise {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }


# Association Table with user-submittable attribute 
class WorkoutExercise(db.Model, SerializerMixin):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    sets = db.Column(db.Integer)  # User-submittable attribute
    reps = db.Column(db.Integer)  # User-submittable attribute  
    weight = db.Column(db.Float)  # User-submittable attribute (in kg/lbs)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"))
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"))

    # Relationships
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    serialize_rules = ("-workout.workout_exercises", "-exercise.workout_exercises")

    # Validations
    @validates('sets')
    def validate_sets(self, key, sets):
        if sets is not None and sets <= 0:
            raise ValueError("Sets must be positive")
        return sets

    @validates('reps')
    def validate_reps(self, key, reps):
        if reps is not None and reps <= 0:
            raise ValueError("Reps must be positive")
        return reps

    @validates('weight')
    def validate_weight(self, key, weight):
        if weight is not None and weight < 0:
            raise ValueError("Weight cannot be negative")
        return weight

    def __repr__(self):
        return f"<WorkoutExercise {self.exercise.name} in {self.workout.type}>"

    def to_dict(self):
        return {
            'id': self.id,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'workout_id': self.workout_id,
            'exercise_id': self.exercise_id,
            'exercise': self.exercise.to_dict() if self.exercise else None
        }