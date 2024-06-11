import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Create an SQLite database connection
conn = sqlite3.connect('sports_predictions.db')
cursor = conn.cursor()

# Define admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS games(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  actual_score_team1 INTEGER,
                  actual_score_team2 INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  game_id INTEGER NOT NULL,
                  predicted_score_team1 INTEGER,
                  predicted_score_team2 INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(game_id) REFERENCES games(id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  total_points INTEGER)''')

# Commit the changes
conn.commit()

def get_flag_image(country):
    country_flag = {
        "Duitsland": "flags/duitsland.png",
        "Schotland": "flags/schotland.png",
        "Hongarije": "flags/hongarije.png",
        "Zwitserland": "flags/zwitserland.png",
        "Spanje": "flags/spanje.png",
        "Kroatië": "flags/kroatie.png",
        "Italië": "flags/italie.png",
        "Albanië": "flags/albanie.png",
        "Slovenië": "flags/slovenie.png",
        "Denemarken": "flags/denemarken.png",
        "Servië": "flags/servie.png",
        "Engeland": "flags/engeland.png",
        "Polen": "flags/polen.png",
        "Nederland": "flags/nederland.png",
        "Oostenrijk": "flags/oostenrijk.png",
        "Frankrijk": "flags/frankrijk.png",
        "België": "flags/belgie.png",
        "Slowakije": "flags/slowakije.png",
        "Roemenië": "flags/roemenie.png",
        "Oekraïne": "flags/oekraine.png",
        "Turkije": "flags/turkije.png",
        "Georgië": "flags/georgie.png",
        "Portugal": "flags/portugal.png",
        "Tsjechië": "flags/tsjechie.png"
    }
    return country_flag.get(country, "flags/default.png")
    

# List of games for Euro 2024
matches = [
    {"date": "14 juni", "time": "21:00", "team_1": "Duitsland", "team_2": "Schotland", "location": "Munich", "id": 1},
    {"date": "15 juni", "time": "15:00", "team_1": "Hongarije", "team_2":  "Zwitserland", "location": "Cologne", "id": 2},
    {"date": "15 juni", "time": "18:00", "team_1": "Spanje", "team_2": "Kroatië", "location": "Berlin", "id": 3},
    {"date": "15 juni", "time": "21:00", "team_1": "Italië", "team_2": "Albanië", "location": "Dortmund", "id": 4},
    {"date": "16 juni", "time": "15:00", "team_1": "Polen", "team_2": "Nederland", "location": "Hamburg", "id": 5},
    {"date": "16 juni", "time": "18:00", "team_1": "Slovenië", "team_2": "Denemarken", "location": "Stuttgart", "id": 6},
    {"date": "16 juni", "time": "21:00", "team_1": "Servië", "team_2": "Engeland", "location": "Gelsenkirchen", "id": 7},
    {"date": "17 juni", "time": "15:00", "team_1": "Roemenië", "team_2": "Oekraïne", "location": "Munich", "id": 8},
    {"date": "17 juni", "time": "18:00", "team_1": "België", "team_2": "Slowakije", "location": "Frankfurt", "id": 9},
    {"date": "17 juni", "time": "21:00", "team_1": "Oostenrijk", "team_2": "Frankrijk", "location": "Düsseldorf", "id": 10},
    {"date": "18 juni", "time": "18:00", "team_1": "Turkije", "team_2": "Georgië", "location": "Dortmund", "id": 11},
    {"date": "18 juni", "time": "21:00", "team_1": "Portugal", "team_2": "Tsjechië", "location": "Leipzig", "id": 12},
    {"date": "19 juni", "time": "15:00", "team_1": "Kroatië", "team_2": "Albanië", "location": "Hamburg", "id": 13},
    {"date": "19 juni", "time": "18:00", "team_1": "Duitsland", "team_2": "Hongarije", "location": "Stuttgart", "id": 14},
    {"date": "19 juni", "time": "21:00", "team_1": "Schotland", "team_2": "Zwitserland", "location": "Cologne", "id": 15},
    {"date": "20 juni", "time": "15:00", "team_1": "Slovenië", "team_2": "Servië", "location": "Munich", "id": 16},
    {"date": "20 juni", "time": "18:00", "team_1": "Denemarken", "team_2": "Engeland", "location": "Frankfurt", "id": 17},
    {"date": "20 juni", "time": "21:00", "team_1": "Spanje", "team_2": "Italië", "location": "Gelsenkirchen", "id": 18},
    {"date": "21 juni", "time": "15:00", "team_1": "Slowakije", "team_2": "Oekraïne", "location": "Düsseldorf", "id": 19},
    {"date": "21 juni", "time": "18:00", "team_1": "Polen", "team_2": "Oostenrijk", "location": "Berlin", "id": 20},
    {"date": "21 juni", "time": "21:00", "team_1": "Nederland", "team_2": "Frankrijk", "location": "Leipzig", "id": 21},
    {"date": "22 juni", "time": "15:00", "team_1": "Georgië", "team_2": "Tsjechië", "location": "Hamburg", "id": 22},
    {"date": "22 juni", "time": "18:00", "team_1": "Turkije", "team_2": "Portugal", "location": "Dortmund", "id": 23},
    {"date": "22 juni", "time": "21:00", "team_1": "België", "team_2": "Roemenië", "location": "Cologne", "id": 24},
    {"date": "23 juni", "time": "21:00", "team_1": "Zwitserland", "team_2": "Duitsland", "location": "Frankfurt", "id": 25},
    {"date": "23 juni", "time": "21:00", "team_1": "Schotland", "team_2": "Hongarije", "location": "Stuttgart", "id": 26},
    {"date": "24 juni", "time": "21:00", "team_1": "Kroatië", "team_2": "Italië", "location": "Leipzig", "id": 27},
    {"date": "24 juni", "time": "21:00", "team_1": "Albanië", "team_2": "Spanje", "location": "Düsseldorf", "id": 28},
    {"date": "25 juni", "time": "18:00", "team_1": "Nederland", "team_2": "Oostenrijk", "location": "Berlin", "id": 29},
    {"date": "25 juni", "time": "18:00", "team_1": "Frankrijk", "team_2": "Polen", "location": "Dortmund", "id": 30},
    {"date": "25 juni", "time": "21:00", "team_1": "Engeland", "team_2": "Slovenië", "location": "Cologne", "id": 31},
    {"date": "25 juni", "time": "21:00", "team_1": "Denemarken", "team_2": "Servië", "location": "Munich", "id": 32},
    {"date": "26 juni", "time": "18:00", "team_1": "Slowakije", "team_2": "Roemenië", "location": "Frankfurt", "id": 33},
    {"date": "26 juni", "time": "18:00", "team_1": "Oekraïne", "team_2": "België", "location": "Stuttgart", "id": 34},
    {"date": "26 juni", "time": "21:00", "team_1": "Tsjechië", "team_2": "Turkije", "location": "Hamburg", "id": 35},
    {"date": "26 juni", "time": "21:00", "team_1": "Georgië", "team_2": "Portugal", "location": "Gelsenkirchen", "id": 36},
]

def register():
    st.title("Aanmelden")
    new_user = st.text_input("Gebruikersnaam")
    new_password = st.text_input("Wachtwoord", type="password")
    if st.button("Register"):
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_password))
            conn.commit()
            st.success("You have successfully created an account")
        except sqlite3.IntegrityError:
            st.error("Username already exists")

def login():
    st.title("Inloggen")
    user = st.text_input("Gebruikersnaam")
    pw = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        user_data = cursor.fetchone()
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user_id = user_data[0]
            st.success("Login succesvol! klik nogmaals op inloggen om door te gaan")
        else:
            st.error("Incorrect username or password")
            

def admin_login():
    st.title("Admin Login")
    admin_user = st.text_input("Admin Username")
    admin_pw = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if admin_user == ADMIN_USERNAME and admin_pw == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Admin logged in successfully")
        else:
            st.error("Incorrect admin username or password")
        

def predictions():
    # Retrieve the user's predictions
    user_id = st.session_state.user_id
    predictions_to_save = []
    cursor.execute('''
        SELECT game_id, predicted_score_team1, predicted_score_team2 
        FROM predictions 
        WHERE user_id = ?
    ''', (user_id,))
    user_predictions = cursor.fetchall()
    
    # Create a dictionary to easily lookup user predictions by game_id
    user_predictions_dict = {prediction[0]: (prediction[1], prediction[2]) for prediction in user_predictions}
    #st.write(user_predictions_dict)
    st.title("Voorspel de Wedstrijden")
    
    
    date = matches[0].get('date')
    st.subheader("14 juni")

    # Display each match with flags
    for match in matches:
        match_date_split = match['date'].split()
        if match_date_split[1] == "juni":
            match_date = datetime(2024, 6, int(match_date_split[0]))
        else:
            match_date = datetime(2024, 7, int(match_date_split[0]))
        
        match_time = int(match['time'].split(sep=':')[0])
        cutoff_time = match_date + timedelta(hours=match_time)
        current_time = datetime.now()
    
        if match['date'] != date:
            st.markdown("""---""") 
            st.subheader(f"**{match['date']}**")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.image(get_flag_image(match['team_1']), width=100)
        if current_time > cutoff_time:
            with col2:
                st.markdown(f"**{match['team_1']}**")
                if match['id'] in user_predictions_dict.keys():
                    score_team1 = user_predictions_dict[match['id']][0]
                    st.write(f"**{user_predictions_dict[match['id']][0]}**")
                else:
                    score_team1 = 0
                    st.write("**0**")
            with col3:
                st.markdown(f"**{match['team_2']}**")
                if match['id'] in user_predictions_dict.keys():                
                    score_team2 = user_predictions_dict[match['id']][1]
                    st.write(f"**{user_predictions_dict[match['id']][1]}**")
                else:
                    score_team2 = 0
                    st.write("**0**")
        else:
            with col2:
                st.markdown(f"**{match['team_1']}**")
                if match['id'] not in user_predictions_dict.keys():                
                    score_team1 = st.number_input(f"**{match['id']}**" + "_home", min_value=0, label_visibility="hidden")
                else:
                    score_team1 = st.number_input(f"**{match['id']}**" + "_home", min_value=0, label_visibility="hidden", value=user_predictions_dict[match['id']][0])
            with col3:
                st.markdown(f"**{match['team_2']}**")
                if match['id'] not in user_predictions_dict.keys():                
                    score_team2 = st.number_input(f"**{match['id']}**" + "_away", min_value=0, label_visibility="hidden")
                else:
                    score_team2 = st.number_input(f"**{match['id']}**" + "_away", min_value=0, label_visibility="hidden", value=user_predictions_dict[match['id']][1])
        with col4:
            st.image(get_flag_image(match['team_2']), width=100)
        
        predictions_to_save.append((user_id, match['id'], score_team1, score_team2))
        #st.write(predictions_to_save)
        date = match['date']
        st.text("")
        st.text("")

    
    # Submit button to save predictions
    
    if st.button("Voorspellingen Opslaan"):
        for prediction in predictions_to_save:
            user_id, game_id, score_team1, score_team2 = prediction
            #st.write("user:", user_id)
            #st.write("game:", game_id)
            
            cursor.execute('''
                SELECT id FROM predictions WHERE user_id = ? AND game_id = ?
            ''', (user_id, game_id))
            prediction_id = cursor.fetchone()
            #st.write("prediction:", prediction_id)
            

            if prediction_id:
                cursor.execute('''
                    UPDATE predictions 
                    SET predicted_score_team1 = ?, predicted_score_team2 = ?
                    WHERE id = ?
                ''', (score_team1, score_team2, prediction_id))
            else:
                cursor.execute('''
                    INSERT INTO predictions (user_id, game_id, predicted_score_team1, predicted_score_team2)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, game_id, score_team1, score_team2))
            
        
        conn.commit()
        st.success("Alle voorspellingen zijn succesvol opgeslagen!")
    

def rules():
    st.title("Spelregels")
    st.write("""
    Welkom in de AH Zandvoort EK poule!
    
    ## Hoe werkt het:
        
    - Maak eerst een account aan of log in om mee te doen.
    - Vul voor elke wedstrijd jouw voorspelling in en vergeet niet op "Voorspellingen opslaan" te drukken onderaan de pagina.
    Zonder hierop te drukken, worden je aanpassingen niet opgeslagen.
    - Je kan je uitslag aanpassen tot aan de aftrap van de wedstrijd. Hierna is dit niet meer mogelijk.
    - De stand die telt is de stand die na een eventuele verlenging op het bord staat. Penalties zijn niet van belang.

    ## Puntentelling:
    - Uitslag exact goed: 100 punten
    - Juiste winnaar: 50 point
    - Juist aantal doelpunten voor een van de teams: 10 punten
    - NB: Een juiste winnaar met een juist aantal doelpunten voor één van de teams levert dus 60 punten op. Exacte uistslagen zullen niet meer dan 100 punten opleveren.
    """)
    st.write("")
    st.write("Heel veel plezier en succes!")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def show_login_register():
    st.sidebar.image("AH.png", width=100)
    st.sidebar.title("Navigatie")
    choice = st.sidebar.radio("Ga naar", ["Inloggen", "Aanmelden", "Regels"])

    if choice == "Inloggen":
        login()
    elif choice == "Aanmelden":
        register()
    elif choice == "Regels":
        rules()


def enter_scores():
    st.title("Enter Match Scores")
    
    for match in matches:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.image(get_flag_image(match['team_1']), width=100)
        with col2:
            st.markdown(f"**{match['team_1']}**")
            score_team1 = st.number_input(f"**{match['id']}**" + "_home_actual", min_value=0, label_visibility="hidden")
        with col3:
            st.markdown(f"**{match['team_2']}**")
            score_team2 = st.number_input(f"**{match['id']}**" + "_away_actual", min_value=0, label_visibility="hidden")
        with col4:
            st.image(get_flag_image(match['team_2']), width=100)
        
        
        if st.button("Score bevestigen", key=f"{match['id']}_save"):
            cursor.execute('''
                UPDATE games 
                SET actual_score_team1 = ?, actual_score_team2 = ? 
                WHERE id = ?
            ''', (score_team1, score_team2, match['id']))
            conn.commit()
            st.success(f"Scores for {match['team_1']} vs {match['team_2']} saved successfully!")
            update_scores_and_leaderboard()
            
            
def fetch_user_scores(user_id):
    cursor.execute('''
        SELECT scores.total_points
        FROM scores
        WHERE scores.user_id = ?
    ''', (user_id,))
    scores = cursor.fetchall()
    
    cursor.execute('''
        SELECT users.username
        FROM users
        WHERE users.id = ?
        ''', (user_id,))
    username = cursor.fetchall()
    return (username, scores)


def calculate_points():
    cursor.execute('''
        SELECT users.id, users.username
        FROM users
    ''')
    players = cursor.fetchall()
    #st.write(players)
    for player in players:
        prediction_user_id = player[0]
        total_points_ = 0
        for match in matches:
            cursor.execute('''
                SELECT predictions.id, predictions.predicted_score_team1, predictions.predicted_score_team2
                FROM predictions
                WHERE predictions.game_id = ? AND predictions.user_id = ?
            ''',(match['id'], player[0]))
            predictions = cursor.fetchall()
            #st.write("Predictions:", predictions)
        
            cursor.execute('''
                SELECT games.actual_score_team1, games.actual_score_team2
                FROM games
                Where games.id = ?
            ''',(match['id'],))
            results = cursor.fetchall()
            #st.write(results)
            #st.write("Results:", results)
            
            if predictions:
                predicted_score_team1 = predictions[0][1]
                predicted_score_team2 = predictions[0][2]
                actual_score_team1 = results[0][0]
                actual_score_team2 = results[0][1]
                #st.write("prediction:", predicted_score_team1, predicted_score_team2)
                #st.write("Results:", actual_score_team1, actual_score_team2)
                
                points_awarded = 0
                if predicted_score_team1 is not None and predicted_score_team2 is not None and actual_score_team1 is not None and actual_score_team2 is not None:
                    if predicted_score_team1 == actual_score_team1 and predicted_score_team2 == actual_score_team2:
                        points_awarded = 100
                    elif np.sign(predicted_score_team1 - predicted_score_team2) == np.sign(actual_score_team1 - actual_score_team2):
                        if predicted_score_team1 == actual_score_team1 or predicted_score_team2 == actual_score_team2:
                            points_awarded = 60
                        else:
                            points_awarded = 50
                    elif predicted_score_team1 == actual_score_team1 or predicted_score_team2 == actual_score_team2:
                        points_awarded = 10
                total_points_ += points_awarded
                #st.write("Points:", points_awarded, total_points_)
        
        cursor.execute('''
            SELECT total_points
            FROM scores
            WHERE user_id = ?
        ''', (prediction_user_id,))
        row = cursor.fetchone()
    
        if row is None:
            cursor.execute('''
                INSERT INTO scores (user_id, total_points)
                VALUES (?,?)
            ''', (prediction_user_id, total_points_))
        else:
            cursor.execute('''
                UPDATE scores
                SET total_points = ?
                WHERE user_id = ?
            ''', (total_points_, prediction_user_id))
        conn.commit()



def leaderboard():
    cursor.execute('''
        SELECT users.id
        FROM users
        ''')
    users = cursor.fetchall()
    st.title("Klassement")
    user_scores = []
    for i in range(len(users)):
        user_scores.append(fetch_user_scores(users[i][0]))
    
    user_scores.sort(reverse=True, key=sortingHelp)
    
    if not user_scores:
        st.write("De stand is beschikbaar vanaf de eerste speeldag")
        return
    
    df = pd.DataFrame(user_scores, columns=['Username', 'Total Points'])
    
    st.dataframe(df)

def sortingHelp(e):
    return e[1][0][0]
    

def update_scores_and_leaderboard():
    calculate_points()
    leaderboard() 

def main_app():
    st.sidebar.image("AH.png", width=100)
    st.sidebar.title("Navigatie")
    if st.session_state.admin_logged_in:
        page = st.sidebar.radio("Ga naar", ["Klassement", "Regels", "Scores doorgeven"])
    else:
        page = st.sidebar.radio("Ga naar", ["Voorspellingen", "Klassement", "Regels"])

    if page == "Voorspellingen":
        predictions()
    elif page == "Klassement":
        leaderboard()
    elif page == "Regels":
        rules()
    elif page == "Scores doorgeven":
        enter_scores()
        
    
    
        
        
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    show_login_register()
    
   
for i in range(10):
    st.text("")    
st.markdown("***")
    
if st.session_state.admin_logged_in:
    main_app()
elif st.session_state.logged_in:
    pass
else:
    admin_login()
