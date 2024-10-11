from flask import Flask, request, jsonify
import pandas as pd
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Дані користувачів і оцінок фільмів
ratings_data = [
    {"user_id": "user1", "movie_id": "movie1", "rating": 5},
    {"user_id": "user1", "movie_id": "movie2", "rating": 3},
    {"user_id": "user2", "movie_id": "movie1", "rating": 4},
    {"user_id": "user2", "movie_id": "movie3", "rating": 5},
    {"user_id": "user3", "movie_id": "movie2", "rating": 4},
    {"user_id": "user3", "movie_id": "movie3", "rating": 3}
]

df = pd.DataFrame(ratings_data)

# Створюємо матрицю користувачів і фільмів
user_movie_matrix = df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)

# Функція для рекомендацій
def recommend_movies(user_id, n_neighbors=2, top_n=5):
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
    model_knn.fit(user_movie_matrix.values)

    user_index = user_movie_matrix.index.get_loc(user_id)
    distances, indices = model_knn.kneighbors([user_movie_matrix.iloc[user_index].values], n_neighbors=n_neighbors+1)
    similar_users = indices.flatten()[1:]

    rated_movies = set(df[df['user_id'] == user_id]['movie_id'])
    all_movies = set(df['movie_id'])
    unrated_movies = list(all_movies - rated_movies)

    movie_scores = {}
    for similar_user in similar_users:
        similar_user_id = user_movie_matrix.index[similar_user]
        for movie_id in unrated_movies:
            movie_rating = user_movie_matrix.loc[similar_user_id, movie_id]
            if movie_id not in movie_scores:
                movie_scores[movie_id] = movie_rating
            else:
                movie_scores[movie_id] += movie_rating

    recommended_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [movie[0] for movie in recommended_movies]

# Роут для рейтингу
@app.route('/rate', methods=['POST'])
def rate_movie():
    data = request.json
    new_rating = {"user_id": data['user_id'], "movie_id": data['movie_id'], "rating": data['rating']}
    global df
    df = df.append(new_rating, ignore_index=True)
    global user_movie_matrix
    user_movie_matrix = df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
    return jsonify({"message": "Rating added successfully!"}), 200

# Роут для рекомендацій
@app.route('/recommend', methods=['POST'])
def get_recommendation():
    data = request.json
    user_id = data['user_id']
    recommended_movies = recommend_movies(user_id)
    return jsonify({"recommended_movies": recommended_movies}), 200

if __name__ == '__main__':
    app.run(debug=True)
