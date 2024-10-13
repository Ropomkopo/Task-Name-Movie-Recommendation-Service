from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Створення DataFrame на основі даних
ratings_data = [
    {"user_id": "user1", "movie_id": "test1", "rating": 5},
    {"user_id": "user2", "movie_id": "test2", "rating": 3},
    {"user_id": "user3", "movie_id": "test3", "rating": 4},
    {"user_id": "user4", "movie_id": "test1", "rating": 5},
    {"user_id": "user5", "movie_id": "test4", "rating": 4},
    {"user_id": "user6", "movie_id": "test2", "rating": 3},
    {"user_id": "user3", "movie_id": "test1", "rating": 5},
    {"user_id": "user7", "movie_id": "test5", "rating": 4},
    {"user_id": "user8", "movie_id": "test6", "rating": 5},
]

ratings_df = pd.DataFrame(ratings_data)

@app.route('/all_data', methods=['GET'])
def get_all_data():
    return jsonify({"message": "All data retrieved successfully!", "data": ratings_data}), 200

# API маршрут для рекомендації фільмів
@app.route('/recommend', methods=['GET'])
def recommend_movies():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "Please provide a 'user_id'."}), 400

        # Фільтруємо фільми, які оцінив поточний користувач
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]

        if user_ratings.empty:
            return jsonify({"message": "User not found or no ratings for this user."}), 404

        # Знаходимо інших користувачів, які поставили такі ж оцінки тим самим фільмам
        similar_users = ratings_df[
            (ratings_df['movie_id'].isin(user_ratings['movie_id'])) &
            (ratings_df['rating'].isin(user_ratings['rating'])) &
            (ratings_df['user_id'] != user_id)
        ]['user_id'].unique()

        # Шукаємо фільми, які оцінювали схожі користувачі, але які ще не оцінив поточний користувач
        recommended_movies_df = ratings_df[
            (ratings_df['user_id'].isin(similar_users)) &
            (~ratings_df['movie_id'].isin(user_ratings['movie_id'])) &
            (ratings_df['rating'] >= 4)  # Рекомендації для фільмів з рейтингом >= 4
        ]

        # Вибираємо топ 5 фільмів
        top_recommended_movies = recommended_movies_df.sort_values(by='rating', ascending=False)['movie_id'].unique()[:5]

        return jsonify({
            "user_id": user_id,
            "recommended_movies": list(top_recommended_movies)
        })
    
    except ValueError:
        return jsonify({"error": "Invalid user_id. Please provide a valid user_id."}), 400

# API маршрут для додавання фільму з рейтингом
@app.route('/movies/new_movie', methods=['POST'])
def add_movie_rating():
    global ratings_df
    data = request.get_json()

    if not data or 'user_id' not in data or 'movie_id' not in data or 'rating' not in data:
        return jsonify({"error": "Please provide 'user_id', 'movie_id', and 'rating'"}), 400

    # Створення нового запису
    new_rating = {
        "user_id": data['user_id'],
        "movie_id": data['movie_id'],
        "rating": data['rating']
    }

    # Додавання запису до DataFrame
    ratings_df = ratings_df._append(new_rating, ignore_index=True)  # Використання DataFrame append

    # Відповідь із підтвердженням
    return jsonify({"message": "Movie rating added successfully", "new_rating": new_rating}), 201


if __name__ == '__main__':
    app.run(debug=True)
