from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection 
import sqlite3
import pickle 

app = Flask(__name__)
CORS(app)


MODEL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'full_model_bundle.pkl')
with open(MODEL_PATH, 'rb') as f:
    bundle = pickle.load(f)
    
print("Keys inside pkl:", bundle.keys())

kmeans = bundle['kmeans']
scaler = bundle['scaler']
le_cuisine = bundle['le_cuisine']
le_city = bundle['le_city']
clustered_df = bundle['df']  # Use this instead of loading CSV


df = clustered_df.copy()


@app.route('/')
def home():
    return jsonify({"message": "Zomato Recommendation API is live!"})

@app.route('/all_clusters', methods=['GET'])
def get_all_data():
    return df.to_json(orient='records')


@app.route('/recommend', methods=['GET'])
def recommend():
    cuisine = request.args.get('cuisine', '').strip()
    city = request.args.get('city', '').strip()
    rating = request.args.get('min_rating', '')
    cost = request.args.get('max_cost', '')

    if not cuisine or not city:
        return jsonify({"error": "Cuisine and City are required"}), 400

    try:
        cuisine_encoded = le_cuisine.transform([cuisine])[0]
        city_encoded = le_city.transform([city])[0]
    except:
        return jsonify({"error": "Cuisine or City not recognized"}), 400

    try:
        rating = float(rating) if rating else 0
        cost = float(cost) if cost else 1e9
    except:
        rating = 0
        cost = 1e9

    input_data = pd.DataFrame([{
        'Cuisine_Encoded': cuisine_encoded,
        'Average_Cost_for_two': cost,
        'Rating': rating,
        'Votes': 100,  # default
        'City_Encoded': city_encoded
    }])

    input_scaled = scaler.transform(input_data)
    predicted_cluster = kmeans.predict(input_scaled)[0]

    result_df = clustered_df[clustered_df['Cluster'] == predicted_cluster]
    result_df = result_df[result_df['Rating'] >= rating]
    result_df = result_df[result_df['Average_Cost_for_two'] <= cost]

    if result_df.empty:
        return jsonify({"message": "No restaurants found in this cluster."}), 404

    recommendations = result_df.sample(n=min(10, len(result_df)), random_state=42)
    return recommendations.to_json(orient='records')    

@app.route('/cuisines', methods=['GET'])
def get_cuisines():
    # cuisine_lists = df['Cuisines'].dropna().str.split(',').tolist()
    cuisine_lists=df['Cuisines'].dropna().str.split(r'[|,]').tolist()
    flat_cuisines = [c.strip() for sublist in cuisine_lists for c in sublist]
    unique_cuisines = sorted(list(set(flat_cuisines)))
    return jsonify(unique_cuisines)

@app.route('/cities', methods=['GET'])
def get_cities():
    cities = df['City'].dropna().unique().tolist()
    return jsonify(sorted(cities))

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '').strip().lower()
    user_id = request.args.get('user_id')

    print("🔍 Received search query:", keyword)
    print("👤 User ID:", user_id)

    if not keyword:
        return jsonify([])

    # Log search
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO search_history (user_id, query) VALUES (?, ?)", (user_id, keyword))
            conn.commit()
            conn.close()
            print("✅ Search logged to DB.")
        except Exception as e:
            print("❌ DB Logging Error:", e)

    # Try to find matching cuisine
    matched_cuisine = None
    for cuisine in clustered_df['Cuisines'].dropna().unique():
        if keyword in cuisine.lower():
            matched_cuisine = cuisine.split(',')[0].strip().lower()
            break

    print("🔎 Matched cuisine from dataset:", matched_cuisine)

    if matched_cuisine is None:
        print("⚠ No matching cuisine found in dataset.")
        return jsonify([])

    try:
        cuisine_encoded = le_cuisine.transform([matched_cuisine])[0]
        print("✅ Encoded cuisine:", cuisine_encoded)
    except Exception as e:
        print("❌ Cuisine encoding failed:", e)
        return jsonify([])

    # Default city
    default_city = 'delhi'
    try:
        city_encoded = le_city.transform([default_city])[0]
    except:
        city_encoded = 0

    input_data = pd.DataFrame([{
        'Cuisine_Encoded': cuisine_encoded,
        'Average_Cost_for_two': 500,
        'Rating': 4.0,
        'Votes': 200,
        'City_Encoded': city_encoded
    }])

    input_scaled = scaler.transform(input_data)
    predicted_cluster = kmeans.predict(input_scaled)[0]

    print("🔢 Predicted cluster:", predicted_cluster)

    cluster_matches = clustered_df[clustered_df['Cluster'] == predicted_cluster]
    print("📊 Found rows in cluster:", len(cluster_matches))

    final_matches = cluster_matches[cluster_matches['Cuisines'].str.lower().str.contains(keyword, na=False)]
    print("🎯 Final matched rows:", len(final_matches))

    if final_matches.empty:
        final_matches = cluster_matches
        print("🔁 Falling back to all cluster rows")

    if final_matches.empty:
        print("❌ No results even after fallback")
        return jsonify([])

    results = final_matches.sample(n=min(10, len(final_matches)), random_state=42)
    print("✅ Returning", len(results), "results")
    return jsonify(results.to_dict(orient='records'))

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





# @app.route('/search', methods=['GET'])
# def search():
#     keyword = request.args.get('q', '').strip().lower()
#     user_id = request.args.get('user_id')
#     max_cost = request.args.get('max_cost')
#     min_rating = request.args.get('min_rating')

#     # Log search history
#     if user_id and keyword:
#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO search_history (user_id, query) VALUES (?, ?)", (user_id, keyword))
#             conn.commit()
#         except Exception as e:
#             print("History log error:", e)
#         finally:
#             conn.close()

#     # Start with all data if no keyword, else filter by keyword
#     if keyword:
#         matched_df = df[
#             df['RestaurantName'].str.lower().str.contains(keyword, na=False) |
#             df['Cuisines'].str.lower().str.contains(keyword, na=False)
#         ]
#     else:
#         matched_df = df.copy()

#     # Apply cost filter if present
#     if max_cost:
#         try:
#             matched_df = matched_df[matched_df['Average_Cost_for_two'] <= float(max_cost)]
#         except ValueError:
#             pass

#     # Apply rating filter if present
#     if min_rating:
#         try:
#             matched_df = matched_df[matched_df['Rating'] >= float(min_rating)]
#         except ValueError:
#             pass

#     if matched_df.empty:
#         return jsonify([])

#     results = matched_df.sample(n=min(10, len(matched_df)), random_state=42)
#     return jsonify(results.to_dict(orient='records'))




# @app.route('/search', methods=['GET'])
# def search():
#     keyword = request.args.get('q', '').strip().lower()
#     user_id = request.args.get('user_id')

#     if not keyword:
#         return jsonify([])

#     # Safe search history logging
#     if user_id:
#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO search_history (user_id, query) VALUES (?, ?)", (user_id, keyword))
#             conn.commit()
#             conn.close()
#         except Exception as e:
#             print("History log error:", e)  # Log error, but don't crash the route

#     matched_df = df[
#         df['RestaurantName'].str.lower().str.contains(keyword, na=False) |
#         df['Cuisines'].str.lower().str.contains(keyword, na=False)
#     ]

#     if matched_df.empty:
#         return jsonify([])

#     results = matched_df.sample(n=min(10, len(matched_df)), random_state=42)
#     return jsonify(results.to_dict(orient='records'))






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
        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

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


# @app.route('/history_recommend', methods=['GET'])
# def history_recommend():
#     user_id = request.args.get("user_id")

#     if not user_id:
#         return jsonify([])

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT query FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
#         past_queries = [row[0] for row in cursor.fetchall()]
#         conn.close()
#     except:
#         return jsonify([])

#     if not past_queries:
#         return jsonify([])

#     # Debug print
#     print("Past queries:", past_queries)

#     filtered_df = df[df['Cuisines'].str.lower().apply(
#         lambda x: any(q.lower() in x for q in past_queries if q)
#     )]

#     if filtered_df.empty:
#         return jsonify([])  # or return fallback

#     recommendations = filtered_df.sample(n=min(10, len(filtered_df)), random_state=42)
#     return jsonify({
#     "recommendations": recommendations.to_dict(orient='records'),
#     "based_on_queries": past_queries
# })


@app.route('/history_recommend', methods=['GET'])
def history_recommend():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"recommendations": [], "based_on_queries": []})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT query FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
    except Exception as e:
        print("❌ Error in DB:", e)
        return jsonify({"recommendations": [], "based_on_queries": []})

    if not row:
        return jsonify({"recommendations": [], "based_on_queries": []})

    last_query = row[0].lower()

    matched_df = df[df['Cuisines'].str.lower().str.contains(last_query, na=False)]

    if matched_df.empty:
        return jsonify({"recommendations": [], "based_on_queries": [last_query]})

    recommendations = matched_df.sample(n=min(10, len(matched_df)), random_state=42)
    return jsonify({
        "recommendations": recommendations.to_dict(orient='records'),
        "based_on_queries": [last_query]
    })


if __name__ == "__main__":
    app.run(debug=True)


