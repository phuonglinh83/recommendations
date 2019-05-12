import os

import models
import db_utils
from datetime import datetime

# Create new rating file from activities in database
rating_file = "rating_matrix/ratings_" + datetime.now().strftime("%Y_%m_%d_%H.csv")
os.makedirs(os.path.dirname(rating_file), exist_ok=True)
db_utils.create_rating_csv(rating_file)

# Build and import recommendations
predicted_ratings, topk_recommendations, similar_scores, topk_similars = models.build_recommendations(rating_file, 40)
db_utils.import_recommendations(predicted_ratings, topk_recommendations, similar_scores, topk_similars)