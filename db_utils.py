import pandas as pd
import datetime
from random import random
from itertools import groupby
import psycopg2


def import_activites(input_file):
    conn = psycopg2.connect("dbname='thesis' user='thesis' password='thesispass'")
    cur = conn.cursor()
    cur.execute("DELETE FROM activities")
    cur.execute(build_activity_load_stmt(input_file))
    conn.commit()
    cur.close()

def build_activity_load_stmt(input_file):
    # Load user ratings
    out = open("load_activities.sql", 'w')
    out.write('INSERT INTO activities (user_id, video_id, action, count, last_modified) VALUES')
    input_ratings = pd.read_csv(input_file)
    for index, row in input_ratings.iterrows():
        if index > 0:
            out.write(",")
        print_row(out, row)
    out.write(";")
    out.close()
    return open('load_activities.sql', 'r').read()


def print_row(out, row):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_id = int(row[0])
    video_id = int(row[1])
    rating = int(row[2])
    if rating < 4:
        print_value(out, user_id, video_id, 'WATCH', rating, time)
    elif rating == 4:
        print_value(out, user_id, video_id, 'SAVE', 1, time)
    else:
        rand = random()
        if rand < 0.5:
            print_value(out, user_id, video_id, 'LIKE', 1, time)
        else:
            print_value(out, user_id, video_id, 'SAVE', 1, time)
            out.write(",")
            print_value(out, user_id, video_id, 'WATCH', 1, time)


def print_value(out, user_id, video_id, action, count, time):
    out.write("\n\t(%d, %d, '%s', %d, '%s')" % (user_id, video_id, action, count, time))


def create_rating_csv(output_file):
    output = open(output_file, 'w')
    output.write("user_id,movie_id,value")
    conn = psycopg2.connect("dbname='thesis' user='thesis' password='thesispass'")
    cur = conn.cursor()
    cur.execute("SELECT user_id, video_id, action, count "
                "FROM activities "
                "ORDER BY user_id, video_id, action")

    rows = cur.fetchall()
    ratings = []
    for row in rows:
        user_id = int(row[0])
        video_id = int(row[1])
        action = str(row[2])
        count = int(row[3])

        rating = count * action_to_score(action)
        ratings.append((user_id, video_id, rating))

    for key, group in groupby(ratings, key=lambda x: (x[0], x[1])):
        total = sum(j[2] for j in group)
        final_rating = max(min(total, 5), 0)
        output.write("\n%d,%d,%d" %(key[0], key[1], final_rating))
    output.close()
    cur.close()


def action_to_score(action):
    return 1 if action == 'WATCH' else 4 if action == 'SAVE' else 5


def import_recommendations(predicted_ratings, topk_recommendations, similar_scores, topk_similars):
    conn = psycopg2.connect("dbname='thesis' user='thesis' password='thesispass'")
    cur = conn.cursor()
    cur.execute("DELETE FROM recommendations")
    for i in range(len(topk_recommendations)):
        for j in range(len(topk_recommendations[0])):
            statement = "INSERT INTO recommendations(user_id, video_id, score) VALUES (%d, %d, %f)" % (
                i + 1, topk_recommendations[i][j] + 1, predicted_ratings[i][topk_recommendations[i][j]])
            cur.execute(statement)
    conn.commit()

    cur.execute("DELETE FROM similar_videos")
    for i in range(len(topk_similars)):
        for j in range(len(topk_similars[0])):
            statement = "INSERT INTO similar_videos(video_id, similar_video_id, score) VALUES (%d, %d, %f)" % (
                i + 1, topk_similars[i][j] + 1, similar_scores[i][topk_similars[i][j]])
            cur.execute(statement)
    conn.commit()
    cur.close()

# build_activity_load('LilyVideosRatings.csv', 'load_activities.sql')
