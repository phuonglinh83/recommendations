import numpy as np
import pandas as pd
import matrix_factorization
import psycopg2


def build_model(input_file):
    # Load user ratings
    raw_dataset_df = pd.read_csv(input_file)

    # Convert the running list of user ratings into a matrix
    ratings_df = pd.pivot_table(raw_dataset_df, index='user_id', columns='movie_id', aggfunc=np.max)

    # Apply matrix factorization to find the latent features
    return matrix_factorization.low_rank_matrix_factorization(ratings_df.as_matrix(),
                                                              num_features=15,
                                                              regularization_amount=0.1)


def find_topk_recommendations(row, top_k):
    return (-row).argsort()[:top_k]


def get_user_recommendation(predicted_ratings, top_k):
    return np.apply_along_axis(find_topk_recommendations, 1, predicted_ratings, top_k)


def diff_score(v1, v2):
    difference = v1 - v2
    return np.sum(np.abs(difference))


def diff_score_all(v1, V):
    return np.apply_along_axis(diff_score, 1, V, v1)


def find_topk_similar(row, top_k):
    return row.argsort()[1:top_k + 1]


def get_similar_videos(V, top_k):
    similar_scores = np.apply_along_axis(diff_score_all, 1, V, V)
    return np.apply_along_axis(find_topk_similar, 1, similar_scores, top_k)


def db_import(U, V, predicted_ratings, recommendations):
    conn = psycopg2.connect("dbname='thesis' user='thesis' password='thesispass'")
    cur = conn.cursor()
    cur.execute("DELETE FROM recommendations")
    for i in range(len(recommendations)):
        for j in range(len(recommendations[0])):
            statement = "INSERT INTO recommendations(user_id, video_id, score) VALUES (%d, %d, %f)" % (
                i + 1, recommendations[i][j] + 1, predicted_ratings[i][recommendations[i][j]])
            cur.execute(statement)
    conn.commit()

    V = np.transpose(V)
    similar_scores = np.apply_along_axis(diff_score_all, 1, V, V)
    similars = get_similar_videos(V, 10)

    cur.execute("DELETE FROM similar_videos")
    for i in range(len(similars)):
        for j in range(len(similars[0])):
            statement = "INSERT INTO similar_videos(video_id, similar_video_id, score) VALUES (%d, %d, %f)" % (
                i + 1, similars[i][j] + 1, similar_scores[i][similars[i][j]])
            cur.execute(statement)
    conn.commit()
    cur.close()


def get_categories(input_file):
    categories = pd.read_csv(input_file)
    results = {}
    for index, row in categories.iterrows():
        results[row[0]] = set(map(int, row[1].split('-')))
    return results


def evaluate(predicted_ratings, user_groups, video_groups, top_k):
    recommendations = get_user_recommendation(predicted_ratings, top_k)
    match = 0
    for user in range(len(recommendations)):
        for video in recommendations[user]:
            if video_groups[video + 1] & user_groups[user + 1]:
                match = match + 1
    # print(match)
    return 100 * (0.0 + match) / (top_k * len(user_groups))

top_k = 10
U, V = build_model('LilyVideosRatings.csv')
# Find all predicted ratings by multiplying the U by V
predicted_ratings = np.matmul(U, V)
# recommendations = get_user_recommendation(predicted_ratings, top_k)
# db_import(U, V, predicted_ratings, recommendations)
user_groups = get_categories("user_group.csv")
video_groups = get_categories("video_group.csv")

for top_k in range(1, 31):
    print(top_k, evaluate(predicted_ratings, user_groups, video_groups, top_k))