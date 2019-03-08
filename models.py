import numpy as np
import pandas as pd
import matrix_factorization


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


U, V = build_model('LilyVideosRatings.csv')
# U, V = build_model('movie_ratings.csv')

# print(len(V[0]));

# Find all predicted ratings by multiplying the U by V
predicted_ratings = np.matmul(U, V)

print(predicted_ratings[1])
print(get_user_recommendation(predicted_ratings, 10))


V = np.transpose(V)
print(V[0])
print(V[1])
print(diff_score(V[0], V[1]))
print(diff_score(V[0], V[2]))
print(diff_score_all(V[0], V))
print(get_similar_videos(V, 5))
print(get_similar_videos(U, 10))
