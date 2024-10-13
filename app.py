from flask import Flask, request, jsonify

app = Flask(__name__)

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


@app.route('/all_data', methods=['GET'])
def rate_movie():
    return jsonify({"message": "Rating added successfully!", "data": ratings_data}), 200

    
# API маршрут для рекомендації фільмів
@app.route('/recommend', methods=['GET'])
def recommend_movies():
    try:
        user_id = request.args.get('user_id')
         # Знаходимо фільми, які оцінив поточний користувач
        user_ratings = {r['movie_id']: r['rating'] for r in ratings_data if r['user_id'] == user_id}

        if not user_ratings:
            return jsonify({"message": "User not found or no ratings for this user."}), 404

        # Знаходимо інших користувачів, які поставили ті самі оцінки тим самим фільмам
        similar_users = set()
        for r in ratings_data:
            if r['user_id'] != user_id and r['movie_id'] in user_ratings and r['rating'] == user_ratings[r['movie_id']]:
                similar_users.add(r['user_id'])

        # Шукаємо фільми, які оцінювали схожі користувачі, але які ще не оцінив поточний користувач
        recommended_movies = {}
        for r in ratings_data:
            if r['user_id'] in similar_users and r['movie_id'] not in user_ratings:
                if r['rating'] >= 4:  # Рекомендація для фільмів з високим рейтингом
                    recommended_movies[r['movie_id']] = r['rating']

        # Сортуємо фільми за рейтингом і повертаємо топ 5
        top_recommended_movies = sorted(recommended_movies, key=recommended_movies.get, reverse=True)[:5]

        return jsonify({
            "user_id": user_id,
            "recommended_movies": top_recommended_movies
        })
    
    except ValueError:
        return jsonify({"error": "Invalid user_id. Please provide a valid user_id."}), 400
    

# API маршрут для додавання фільму з рейтингом
@app.route('/movies/new_movie', methods=['POST'])
def add_movie_rating():
    data = request.get_json()

    # Перевірка чи всі необхідні поля передані
    if not data or 'movie_id' not in data or 'rating' not in data:
        return jsonify({"error": "Please provide 'user_id', 'movie_id', and 'rating'"}), 400

    # Створення нового запису
    new_rating = {
        "movie_id": data['movie_id'],
        "rating": data['rating']
    }

    # Додавання запису до масиву
    ratings_data.append(new_rating)

    # Відповідь із підтвердженням
    return jsonify({"message": "Movie rating added successfully", "new_rating": new_rating}), 201


if __name__ == '__main__':
    app.run(debug=True)