import sqlite3
import pandas as pd
import os
from settings import DATABASE_NAME

class FitnessDatabase:
    #de connectie met de database aanmaken
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.create_tables()

    #het aanmaken van de nodige tabellen
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises
            (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts
            (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_exercises 
            (
                id INTEGER PRIMARY KEY,
                workout_id INTEGER,
                exercise_id INTEGER,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                FOREIGN KEY(workout_id) REFERENCES workouts(id),
                FOREIGN KEY(exercise_id) REFERENCES exercises(id)
            )
        ''')
        self.conn.commit()

    #een oefening toevoegen aan de tabel exercises
    def add_exercise(self, name, category):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO exercises (name, category) VALUES (?, ?)", (name, category))
        self.conn.commit()

    #een workout toevoegen aan de tabel workouts
    def add_workout(self, date):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO workouts (date) VALUES (?)", (date,))
        workout_id = cursor.lastrowid
        self.conn.commit()
        return workout_id

    #een oefening aan een workout toevoegen in de tabel workout_exercises
    def add_workout_exercise(self, workout_id, exercise_id, sets, reps, weight):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO workout_exercises (workout_id, exercise_id, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
                       (workout_id, exercise_id, sets, reps, weight))
        self.conn.commit()

    #voeg een workout met bijbehorende oefeningen toe aan de database
    def add_workout_with_exercises(self, date, exercise_data):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO workouts (date) VALUES (?)", (date,))
        workout_id = cursor.lastrowid

        for exercise in exercise_data:
            exercise_id, sets, reps, weight = exercise
            cursor.execute("INSERT INTO workout_exercises (workout_id, exercise_id, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
                           (workout_id, exercise_id, sets, reps, weight))

        self.conn.commit()
        return workout_id

    #haal workouts op voor een specifieke datum en retourneer de resultaten als een Pandas DataFrame
    def get_workouts_dataframe_by_date(self, date):
        cursor = self.conn.cursor()
        cursor.execute("SELECT exercises.name, workout_exercises.sets, workout_exercises.reps, workout_exercises.weight FROM workouts JOIN workout_exercises ON workouts.id = workout_exercises.workout_id JOIN exercises ON workout_exercises.exercise_id = exercises.id WHERE workouts.date = ?", (date,))
        data = cursor.fetchall()

        if data:
            columns = ["Exercise", "Sets", "Reps", "Weight"]
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            return None

    #een lijst van alle oefeningen
    def get_all_exercises(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM exercises")
        return cursor.fetchall()

    #een lijst van alle
    def get_all_workouts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workouts")
        return cursor.fetchall()


def main():
    fitness_db = FitnessDatabase()

    while True:
        print("\n1. Voeg oefening toe")
        print("2. Voeg workout toe met oefeningen")
        print("3. Workout exporteren naar Excel")
        print("4. Toon alle oefeningen")
        print("5. Toon alle workouts")
        print("6. Exit")

        choice = input("Kies een optie: ")

        if choice == "1":
            name = input("Naam van de oefening: ")
            category = input("Categorie van de oefening: ")
            fitness_db.add_exercise(name, category)
            print("Oefening toegevoegd!")

        elif choice == "2":
            date = input("Datum van de workout (formaat: YYYY-MM-DD): ")
            
            exercise_data = []
            while True:
                exercise_id = int(input("ID van de oefening (of voer -1 in om te stoppen): "))
                if exercise_id == -1:
                    break
                
                sets = int(input("Aantal sets: "))
                reps = int(input("Aantal herhalingen: "))
                weight = float(input("Gewicht (in kg): "))
                
                exercise_data.append((exercise_id, sets, reps, weight))

            workout_id = fitness_db.add_workout_with_exercises(date, exercise_data)
            print(f"Workout toegevoegd met ID: {workout_id}")

        elif choice == "3":
            date = input("Datum van de workout (formaat: YYYY-MM-DD): ")
            if date:
                excel_folder = 'workouts'
                os.makedirs(excel_folder, exist_ok=True)  # Maak de map aan als deze niet bestaat
                excel_filename = os.path.join(os.getcwd(), excel_folder, f"workout_{date}.xlsx")
                df = fitness_db.get_workouts_dataframe_by_date(date)

                if df is not None:
                    df.to_excel(excel_filename, index=False)
                    print(f"Workout geëxporteerd naar Excel-bestand: {excel_filename}")
                else:
                    print(f"Geen workouts gevonden voor de opgegeven datum {date}.")
            else:
                print("Ongeldige datum.")



        elif choice == "4":
            exercises = fitness_db.get_all_exercises()
            if exercises:
                print("\nLijst van alle oefeningen:")
                for exercise in exercises:
                    print(exercise)
            else:
                print("Geen oefeningen gevonden.")

        elif choice == "5":
            workouts = fitness_db.get_all_workouts()
            if workouts:
                print("\nLijst van alle workouts:")
                for workout in workouts:
                    print(workout)
            else:
                print("Geen oefeningen gevonden.")


        elif choice == "6":
            break

        else:
            print("Ongeldige keuze. Probeer opnieuw.")
if __name__ == "__main__":
    main()