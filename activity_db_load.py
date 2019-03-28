import pandas as pd
import datetime
from random import random

import psycopg2


def build_activity_load(input_file, output_file):
    # Load user ratings
    out = open(output_file, 'w')
    out.write('INSERT INTO activities (user_id, video_id, action, time) VALUES')
    input_ratings = pd.read_csv(input_file)
    for index, row in input_ratings.iterrows():
        if index > 0:
            out.write(",")
        print_row(out, row)
    out.write(";")


def print_row(out, row):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_id = int(row[0])
    video_id = int(row[1])
    rating = int(row[2])
    if rating < 4:
        print_value(out, user_id, video_id, 'WATCH', time)
        for i in range(1, rating):
            out.write(",")
            print_value(out, user_id, video_id, 'WATCH', time)
    elif rating == 4:
        print_value(out, user_id, video_id, 'SAVE', time)
    else:
        rand = random()
        if rand < 0.5:
            print_value(out, user_id, video_id, 'LIKE', time)
        else:
            print_value(out, user_id, video_id, 'SAVE', time)
            out.write(",")
            print_value(out, user_id, video_id, 'WATCH', time)
    out.close()


def print_value(out, user_id, video_id, action, time):
    out.write("\n\t(%d, %d, '%s', '%s')" % (user_id, video_id, action, time))


def create_rating_csv(output_file):
    output = open(output_file, 'w')
    output.write("user_id,movie_id,value")
    conn = psycopg2.connect("dbname='thesis' user='thesis' password='thesispass'")
    cur = conn.cursor()
    cur.execute("SELECT user_id, video_id, action, count(*) "
                "FROM activities "
                "GROUP BY user_id, video_id, action "
                "ORDER BY user_id, video_id")

    rows = cur.fetchall()
    for row in rows:
        user_id = int(row[0])
        video_id = int(row[1])
        action = str(row[2])
        count = int(row[3])

        rating = min(count * action_to_score(action), 5)
        output.write("\n%d,%d,%d" %(user_id, video_id, rating))
    output.close()


def action_to_score(action):
    return 1 if action == 'WATCH' else 4 if action == 'SAVE' else 5


# build_activity_load('LilyVideosRatings.csv', 'load_activities.sql')
create_rating_csv("rating.txt")
print(action_to_score('WATCH'))
print(action_to_score('SAVE'))
print(action_to_score('LIKE'))
