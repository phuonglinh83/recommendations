import numpy as np
import pandas as pd
import matrix_factorization


def build_model(input_file, features):
    # Load user ratings
    raw_dataset_df = pd.read_csv(input_file)

    # Convert the running list of user ratings into a matrix
    ratings_df = pd.pivot_table(raw_dataset_df, index='user_id', columns='movie_id', aggfunc=np.max)

    # Apply matrix factorization to find the latent features
    U, V = matrix_factorization.low_rank_matrix_factorization(ratings_df.as_matrix(),
                                                              num_features=features,
                                                              regularization_amount=0.1)
    return ratings_df, U, V


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


def build_recommendations(rating_file, top_k):
    original_ratings, U, V = build_model(rating_file, 15)
    # Find all predicted ratings by multiplying the U by V
    predicted_ratings = np.matmul(U, V)
    # Build recommendations
    topk_recommendations = get_user_recommendation(predicted_ratings, top_k)

    V = np.transpose(V)
    similar_scores = np.apply_along_axis(diff_score_all, 1, V, V)
    topk_similars = get_similar_videos(V, top_k)

    return predicted_ratings, topk_recommendations, similar_scores, topk_similars


