from app import app, db
from models import User, Workout, Exercise, WorkoutExercise
from datetime import datetime, timedelta

def seed_data():
    with app.app_context():
        print("Clearing existing data...")
        
        # Clear tables in proper order
        WorkoutExercise.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        User.query.delete()
        db.session.commit()

        # Create users
        users = [
            User(username="fitness_fan", email="fan@example.com"),
            User(username="gym_rat", email="gym@example.com"),
            User(username="yoga_lover", email="yoga@example.com"),
            User(username="runner123", email="runner@example.com")
        ]
        
        for user in users:
            user.set_password("password123")
        
        db.session.add_all(users)
        db.session.commit()

        # Create exercises
        exercises = [
            Exercise(name="Push-ups", category="Strength"),
            Exercise(name="Squats", category="Strength"),
            Exercise(name="Running", category="Cardio"),
            Exercise(name="Cycling", category="Cardio"),
            Exercise(name="Yoga Flow", category="Flexibility"),
            Exercise(name="Plank", category="Core"),
            Exercise(name="Bench Press", category="Strength"),
            Exercise(name="Deadlift", category="Strength"),
            Exercise(name="Jumping Jacks", category="Cardio"),
            Exercise(name="Stretching", category="Flexibility")
        ]

        db.session.add_all(exercises)
        db.session.commit()

        # Create workouts
        workouts = [
            Workout(type="Strength Training", duration=45, calories_burned=400,
                   notes="Chest and triceps day", user_id=users[0].id),
            Workout(type="Cardio", duration=30, calories_burned=300,
                   notes="Morning run", user_id=users[0].id),
            
            Workout(type="Cycling", duration=60, calories_burned=600,
                   notes="Long bike ride", user_id=users[1].id),
            Workout(type="Weight Training", duration=50, calories_burned=450,
                   notes="Leg day", user_id=users[1].id),
            
            Workout(type="Yoga", duration=60, calories_burned=200,
                   notes="Evening yoga flow", user_id=users[2].id),
            Workout(type="Pilates", duration=45, calories_burned=250,
                   notes="Core workout", user_id=users[2].id),
            
            Workout(type="HIIT", duration=25, calories_burned=350,
                   notes="High intensity training", user_id=users[3].id),
            Workout(type="Walking", duration=40, calories_burned=180,
                   notes="Evening walk", user_id=users[3].id)
        ]

        # Add dates to workouts
        for i, workout in enumerate(workouts):
            workout.date = datetime.now() - timedelta(days=i % 7)
        
        db.session.add_all(workouts)
        db.session.commit()

        # Create workout-exercise associations (many-to-many with user-submittable attributes)
        workout_exercises = [
            # Workout 1 exercises
            WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[0].id, sets=3, reps=15, weight=None),
            WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[6].id, sets=4, reps=10, weight=65.0),
            
            # Workout 2 exercises
            WorkoutExercise(workout_id=workouts[1].id, exercise_id=exercises[2].id, sets=1, reps=30, weight=None),
            
            # Workout 3 exercises
            WorkoutExercise(workout_id=workouts[2].id, exercise_id=exercises[3].id, sets=1, reps=60, weight=None),
            
            # Workout 4 exercises
            WorkoutExercise(workout_id=workouts[3].id, exercise_id=exercises[1].id, sets=5, reps=12, weight=85.0),
            WorkoutExercise(workout_id=workouts[3].id, exercise_id=exercises[7].id, sets=4, reps=8, weight=120.0),
            
            # Workout 5 exercises
            WorkoutExercise(workout_id=workouts[4].id, exercise_id=exercises[4].id, sets=1, reps=60, weight=None),
            WorkoutExercise(workout_id=workouts[4].id, exercise_id=exercises[9].id, sets=1, reps=20, weight=None),
            
            # Workout 6 exercises
            WorkoutExercise(workout_id=workouts[5].id, exercise_id=exercises[5].id, sets=3, reps=60, weight=None),
            
            # Workout 7 exercises
            WorkoutExercise(workout_id=workouts[6].id, exercise_id=exercises[8].id, sets=5, reps=20, weight=None),
            WorkoutExercise(workout_id=workouts[6].id, exercise_id=exercises[0].id, sets=4, reps=15, weight=None),
            
            # Workout 8 exercises
            WorkoutExercise(workout_id=workouts[7].id, exercise_id=exercises[2].id, sets=1, reps=40, weight=None)
        ]

        db.session.add_all(workout_exercises)
        db.session.commit()

        print(f"Seeded {len(users)} users, {len(exercises)} exercises, {len(workouts)} workouts, and {len(workout_exercises)} workout-exercise associations.")

# Add CLI command
@app.cli.command("seed-db")
def seed_db_command():
    """Seed the database with sample data"""
    seed_data()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()