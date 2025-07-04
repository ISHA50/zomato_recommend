from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection 
import sqlite3

app = Flask(__name__)
CORS(app)


# Load clustered data
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'zomato_clustered_cleaned.csv')
df = pd.read_csv(DATA_PATH)

# Ensure correct data types
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Average_Cost_for_two'] = pd.to_numeric(df['Average_Cost_for_two'], errors='coerce')
df['Cuisines'] = df['Cuisines'].astype(str)
df['City'] = df['City'].astype(str)

@app.route('/')
def home():
    return jsonify({"message": "Zomato Recommendation API is live!"})

@app.route('/all_clusters', methods=['GET'])
def get_all_data():
    return df.to_json(orient='records')

@app.route('/recommend', methods=['GET'])
def recommend():
    cuisine_query = request.args.get('cuisine', '').strip().lower()
    city_query = request.args.get('city', '').strip().lower()
    min_rating = request.args.get('min_rating')
    max_cost = request.args.get('max_cost')

    filtered_df = df.copy()

    # Partial matching for cuisine
    if cuisine_query:
        filtered_df = filtered_df[filtered_df['Cuisines'].str.lower().str.contains(cuisine_query, na=False)]

    # Partial matching for city
    if city_query:
        filtered_df = filtered_df[filtered_df['City'].str.lower().str.contains(city_query, na=False)]

    # Optional filters: rating and cost
    if min_rating:
        try:
            filtered_df = filtered_df[filtered_df['Rating'] >= float(min_rating)]
        except ValueError:
            pass  # ignore bad input

    if max_cost:
        try:
            filtered_df = filtered_df[filtered_df['Average_Cost_for_two'] <= float(max_cost)]
        except ValueError:
            pass  # ignore bad input

    # If no match found, return fallback suggestions
    if filtered_df.empty:
        fallback = df.sample(n=min(5, len(df)), random_state=42)
        return fallback.to_json(orient='records')

    recommendations = filtered_df.sample(n=min(10, len(filtered_df)), random_state=42)
    return recommendations.to_json(orient='records')

@app.route('/cuisines', methods=['GET'])
def get_cuisines():
    cuisine_lists = df['Cuisines'].dropna().str.split(',').tolist()
    flat_cuisines = [c.strip() for sublist in cuisine_lists for c in sublist]
    unique_cuisines = sorted(list(set(flat_cuisines)))
    return jsonify(unique_cuisines)

@app.route('/cities', methods=['GET'])
def get_cities():
    cities = df['City'].dropna().unique().tolist()
    return jsonify(sorted(cities))

# @app.route('/search', methods=['GET'])
# def search():
#     keyword = request.args.get('q', '').strip().lower()

#     if not keyword:
#         return jsonify([])

#     matched_df = df[
#         df['RestaurantName'].str.lower().str.contains(keyword, na=False) |
#         df['Cuisines'].str.lower().str.contains(keyword, na=False)
#     ]

#     if matched_df.empty:
#         return jsonify([])

#     results = matched_df.sample(n=min(10, len(matched_df)), random_state=42)
#     return results.to_json(orient='records')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '').strip().lower()
    user_id = request.args.get('user_id')

    # Log search history
    if user_id and keyword:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO search_history (user_id, query) VALUES (?, ?)", (user_id, keyword))
            conn.commit()
        except Exception as e:
            print("History log error:", e)
        finally:
            conn.close()

    # Search restaurants
    matched_df = df[
        df['RestaurantName'].str.lower().str.contains(keyword, na=False) |
        df['Cuisines'].str.lower().str.contains(keyword, na=False)
    ]

    if matched_df.empty:
        return jsonify([])

    results = matched_df.sample(n=min(10, len(matched_df)), random_state=42)
    return jsonify(results.to_dict(orient='records'))



@app.route('/default')
def default():
    query = request.args.get("q", "").lower()

    if query == "all" or not query:
        results = df.sample(n=min(12, len(df)))  # random shuffle of all
    else:
        results = df[df['Cuisines'].str.lower().str.contains(query, na=False)]

    return results.to_json(orient='records')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        if conn:
            conn.close()






@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row["password"], password):
        return jsonify({"message": "Login successful", "user_id": row["id"]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route('/history_recommend', methods=['GET'])
def history_recommend():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify([])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT query FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
        past_queries = [row[0] for row in cursor.fetchall()]
        conn.close()
    except:
        return jsonify([])

    if not past_queries:
        return jsonify([])

    # Debug print
    print("Past queries:", past_queries)

    filtered_df = df[df['Cuisines'].str.lower().apply(
        lambda x: any(q.lower() in x for q in past_queries if q)
    )]

    if filtered_df.empty:
        return jsonify([])  # or return fallback

    recommendations = filtered_df.sample(n=min(10, len(filtered_df)), random_state=42)
    return jsonify({
    "recommendations": recommendations.to_dict(orient='records'),
    "based_on_queries": past_queries
})





if __name__ == "__main__":
    app.run(debug=True)
