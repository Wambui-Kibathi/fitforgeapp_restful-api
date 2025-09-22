from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app import api, db
from models import User, Workout, Exercise, WorkoutExercise

# Simple validation functions
def validate_email(email):
    return '@' in email and '.' in email and len(email) > 5

def validate_password(password):
    return len(password) >= 6 if password else False

def validate_username(username):
    return len(username.strip()) >= 3 if username else False