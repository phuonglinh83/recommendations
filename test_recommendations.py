from models import *


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
    return 100 * (0.0 + match) / (top_k * len(user_groups))


def RMSE(real, predicted):
    return np.sqrt(np.nanmean(np.square(real - predicted)))


rating_file = 'LilyVideosRatings.csv'
user_groups = get_categories("user_group.csv")
video_groups = get_categories("video_group.csv")

# Varying number of features, using top 10 recommendations
for num_features in range(1, 21):
    original_ratings, U, V = build_model(rating_file, num_features)
    predicted_ratings = np.matmul(U, V)
    rmse = RMSE(original_ratings, predicted_ratings)
    custom_score = evaluate(predicted_ratings, user_groups, video_groups, 10)
    print(num_features, rmse, custom_score)

# Varying topk, using 15 features
original_ratings, U, V = build_model(rating_file, 15)
predicted_ratings = np.matmul(U, V)
for top_k in range(1, 31):
    custom_score = evaluate(predicted_ratings, user_groups, video_groups, top_k)
    print(top_k, custom_score)
