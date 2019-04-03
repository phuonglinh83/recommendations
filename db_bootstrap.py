import db_utils
import models

rating_file = "LilyVideosRatings.csv"

# Import activities
db_utils.import_activites(rating_file)

# Build and import recommendations
predicted_ratings, topk_recommendations, similar_scores, topk_similars = models.build_recommendations(rating_file, 20)
db_utils.import_recommendations(predicted_ratings, topk_recommendations, similar_scores, topk_similars)
