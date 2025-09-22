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

# Authentication Resources
class Register(Resource):
    def post(self):
        data = request.get_json()

        if not data.get('username') or not data.get('email') or not data.get('password'):
            return {"message": "Username, email, and password are required."}, 400

        if not validate_username(data['username']):
            return {"message": "Username must be at least 3 characters long."}, 400

        if not validate_email(data['email']):
            return {"message": "Invalid email format."}, 400

        if not validate_password(data['password']):
            return {"message": "Password must be at least 6 characters long."}, 400

        try:
            user = User(username=data['username'], email=data['email'])
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "Username or email already exists."}, 409
        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400


class Login(Resource):
    def post(self):
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return {"message": "Username and password are required."}, 400

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = create_access_token(identity=user.id)
            return {
                "access_token": token, 
                "user": user.to_dict(),
                "message": "Login successful"
            }, 200

        return {"message": "Invalid username or password."}, 401

# User Resources
class Users(Resource):
    @jwt_required()
    def get(self):
        users = User.query.all()
        return [user.to_dict() for user in users], 200

class UserById(Resource):
    @jwt_required()
    def get(self, id):
        user = User.query.get_or_404(id)
        return user.to_dict(), 200
    
    @jwt_required()
    def patch(self, id):
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        if 'email' in data:
            if not validate_email(data['email']):
                return {"message": "Invalid email format."}, 400
            user.email = data['email']
        
        try:
            db.session.commit()
            return user.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "Email already exists."}, 409
    
    @jwt_required()
    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully."}, 204

# Workout Resources
class Workouts(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        workouts = Workout.query.filter_by(user_id=current_user_id).order_by(Workout.date.desc()).all()
        return [workout.to_dict() for workout in workouts], 200

    @jwt_required()
    def post(self):
        data = request.get_json()

        if not data.get("type") or not data.get("duration"):
            return {"message": "Workout type and duration are required."}, 400

        try:
            workout = Workout(
                type=data['type'],
                duration=data['duration'],
                calories_burned=data.get('calories_burned'),
                notes=data.get('notes'),
                user_id=get_jwt_identity()
            )
            db.session.add(workout)
            db.session.commit()
            return workout.to_dict(), 201
        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400


class WorkoutById(Resource):
    @jwt_required()
    def get(self, id):
        workout = Workout.query.get_or_404(id)
        if workout.user_id != get_jwt_identity():
            return {"message": "Not authorized to access this workout."}, 403
        return workout.to_dict(), 200

    @jwt_required()
    def patch(self, id):
        workout = Workout.query.get_or_404(id)
        if workout.user_id != get_jwt_identity():
            return {"message": "Not authorized to update this workout."}, 403
            
        data = request.get_json()

        try:
            for key, value in data.items():
                if hasattr(workout, key) and key not in ['id', 'user_id', 'date']:
                    setattr(workout, key, value)
            
            db.session.commit()
            return workout.to_dict(), 200
        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400

    @jwt_required()
    def delete(self, id):
        workout = Workout.query.get_or_404(id)
        if workout.user_id != get_jwt_identity():
            return {"message": "Not authorized to delete this workout."}, 403
            
        db.session.delete(workout)
        db.session.commit()
        return {"message": "Workout deleted successfully."}, 204

# Exercise Resources
class Exercises(Resource):
    def get(self):
        exercises = Exercise.query.all()
        return [exercise.to_dict() for exercise in exercises], 200

    @jwt_required()
    def post(self):
        data = request.get_json()

        if not data.get("name"):
            return {"message": "Exercise name is required."}, 400

        try:
            exercise = Exercise(
                name=data['name'],
                category=data.get('category')
            )
            db.session.add(exercise)
            db.session.commit()
            return exercise.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "Exercise already exists."}, 409
        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400

# WorkoutExercise Resources (Many-to-Many Association)
class WorkoutExercises(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        if not data.get("workout_id") or not data.get("exercise_id"):
            return {"message": "Workout ID and Exercise ID are required."}, 400

        # Verify user owns the workout
        workout = Workout.query.get(data["workout_id"])
        if not workout or workout.user_id != get_jwt_identity():
            return {"message": "Not authorized to modify this workout."}, 403

        try:
            workout_exercise = WorkoutExercise(
                workout_id=data["workout_id"],
                exercise_id=data["exercise_id"],
                sets=data.get('sets'),
                reps=data.get('reps'),
                weight=data.get('weight')
            )
            db.session.add(workout_exercise)
            db.session.commit()
            return workout_exercise.to_dict(), 201
        except ValueError as e:
            db.session.rollback()
            return {"message": str(e)}, 400

class WorkoutExerciseById(Resource):
    @jwt_required()
    def delete(self, id):
        workout_exercise = WorkoutExercise.query.get_or_404(id)
        
        # Verify user owns the workout
        if workout_exercise.workout.user_id != get_jwt_identity():
            return {"message": "Not authorized to delete this exercise."}, 403
            
        db.session.delete(workout_exercise)
        db.session.commit()
        return {"message": "Exercise removed from workout."}, 204

# Route Registration
api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
api.add_resource(Users, "/users")
api.add_resource(UserById, "/users/<int:id>")
api.add_resource(Workouts, "/workouts")
api.add_resource(WorkoutById, "/workouts/<int:id>")
api.add_resource(Exercises, "/exercises")
api.add_resource(WorkoutExercises, "/workout-exercises")
api.add_resource(WorkoutExerciseById, "/workout-exercises/<int:id>")