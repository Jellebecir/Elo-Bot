import os
import mysql.connector
from datetime import date
host = os.environ['HOST']
user = os.environ['USER']
password = os.environ['PASSWORD']
database = os.environ['DATABASE']
port = os.environ['PORT']


def get_all_channel_ids(connection):
    sql = "SELECT table_name " \
          "FROM information_schema.tables " \
          "WHERE table_schema = 'testdatabase';"  # change testdatabase to actual database name
    cursor = connection.cursor()
    cursor.execute(sql)
    results = [id_tuple[0].upper() for id_tuple in cursor.fetchall()]
    cursor.close()
    return results


def insert_match(winner_id, loser_id, channel_id, connection):
    sql = "INSERT INTO {} (winner_id, loser_id, match_date) " \
          "VALUES ('{}', '{}', '{}');" \
        .format(channel_id, winner_id, loser_id, date.today().strftime("%Y-%m-%d"))
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.close()
    print(" - INSERTED MATCH WITH WINNER {} AND LOSER {} INTO TABLE {}".format(winner_id, loser_id, channel_id))


def user_in_table(user_id, channel_id, connection):
    cursor = connection.cursor()
    sql = "SELECT * FROM {} WHERE user_id = '{}';".format(channel_id, user_id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    return len(rows) > 0

def get_user_ranking(user_id, channel_id, connection):
    if user_in_table(user_id, channel_id, connection):
        cursor = connection.cursor()
        sql = "SELECT ranking FROM {} WHERE user_id = '{}'".format(channel_id, user_id)
        cursor.execute(sql)
        results = cursor.fetchall()[0][0]
        cursor.close()
        return results


def create_channel_table(channel_id, connection):
    sql = "CREATE TABLE IF NOT EXISTS {} (" \
          "match_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, " \
          "winner_id VARCHAR(25) NOT NULL" \
          "loser_id VARCHAR(25) NOT NULL" \
          "match_date DATE NOT NULL" \
          ");".format(channel_id)
    cursor = connection.cursor()
    cursor.execute(sql)
    cursor.close()
    print(" - CREATED TABLE FOR CHANNEL {}".format(channel_id))


def both_players_in_table(id_1, id_2, channel_id, connection):
    return user_in_table(id_1, channel_id, connection) and user_in_table(id_2, channel_id, connection)


def get_matches(channel_id, connection):
    match_query = "SELECT * FROM {}".format(channel_id)
    match_cursor = connection.cursor()
    match_cursor.execute(match_query)
    matches = match_cursor.fetchall()
    match_cursor.close()
    return matches


def get_match_users(channel_id, connection):
    user_query = "SELECT winner_id FROM {channel_id}" \
                "UNION" \
                "SELECT loser_id FROM {channel_id};".format(channel_id=channel_id)
    cursor = connection.cursor()
    cursor.execute(user_query)
    results = cursor.fetchall()
    cursor.close()
    return [result[0] for result in results]


def get_player_wins(player_id, matches):
    wins = 0
    for match in matches:
        if match[1] == player_id:
            wins += 1
    return wins


def get_player_losses(player_id, matches):
    losses = 0
    for match in matches:
        if match[2] == player_id:
            losses += 1
    return losses


class DBConnector:
    def __init__(self):
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database,
            pool_name='elo_bot_pool',
            pool_size=5
        )

    def get_history_between_players(self, id_1, id_2, channel_id):
        with self.connection_pool.get_connection() as connection:
            if both_players_in_table(id_1, id_2, channel_id, connection):
                cursor = connection.cursor()
                sql = "SELECT " \
                      "(SELECT COUNT(*) FROM {channel_id} " \
                      "WHERE winner_id = '{user1}' " \
                      "AND loser_id = '{user2}')" \
                      "as p1_win_count," \
                      "(SELECT COUNT(*) FROM {channel_id} " \
                      "WHERE winner_id = '{user2}' " \
                      "AND loser_id = '{user1}')" \
                      "as p2_win_count;" \
                    .format(user1=id_1, user2=id_2, channel_id=channel_id)
                cursor.execute(sql)
                result = cursor.fetchall()[0]
                cursor.close()
                print(" - RETRIEVED HISTORY BETWEEN PLAYERS")
                return {
                    id_1: result[0],
                    id_2: result[1]
                }

    def get_channel_leaderboard(self, channel_id):
        with self.connection_pool.get_connection() as connection:
            matches = get_matches(channel_id, connection)
            players = get_match_users(channel_id, connection)
            rows = []
            for player_id in players:
                wins = get_player_wins(player_id, matches)
                losses = get_player_losses(player_id, matches)
                winrate = wins/(wins+losses) * 100
                rating = [rank[1] for rank in rankings if rank[0] == player_id][0]
                row = [player_id, wins, losses, winrate, rating]
                rows.append(row)
            rows.sort(key=lambda x: x[4], reverse=True)
            print(" - RETRIEVED LEADERBOARD FROM DATABASE")
            return rows

    def get_user_stats(self, user_id, channel_id):
        with self.connection_pool.get_connection() as connection:
            cursor = connection.cursor()
            sql = "SELECT " \
                  "SUM(wins) as total_wins, " \
                  "SUM(losses) as total_losses, " \
                  "SUM(wins)/SUM(losses) as win_ratio " \
                  "FROM (" \
                  "SELECT " \
                  "CASE WHEN winner_id = '{user_id}' THEN winner_id ELSE loser_id END as player, " \
                  "CASE WHEN winner_id = '{user_id}' THEN 1 ELSE 0 END as wins, " \
                  "CASE WHEN loser_id = '{user_id}' THEN 1 ELSE 0 END as losses " \
                  "FROM {channel_id} m " \
                  "WHERE winner_id = '{user_id}' OR loser_id = '{user_id}') " \
                  "as player_stats;".format(user_id=user_id, channel_id=channel_id)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results
