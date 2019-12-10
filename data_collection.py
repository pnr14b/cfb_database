import requests
import json
import sqlite3
from sqlite3 import Error
import pandas as pd

base = "http://api.collegefootballdata.com/"
f = r"cfb_database"


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)


def dbmain():
    database = r"mydb"

    sql_create_matchup_table = """ CREATE TABLE IF NOT EXISTS MATCHUP (
                                        hometeam text ,
                                        awayteam text ,
                                        week integer,
                                        season integer,
                                        PRIMARY KEY(hometeam,awayteam,week,season)
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_matchup_table)

    else:
        print("Error! cannot create the database connection.")
    return conn


def insert(conn, home, away, week, season):
    sql = " INSERT INTO MATCHUP (hometeam,awayteam,week,season) VALUES(?,?,?,?) "
    cur = conn.cursor()
    try:
        cur.execute(sql, (home, away, week, season))
    except sqlite3.IntegrityError as e:
        # print ("**********"+home +away + str(week) +str(season))
        pass
    conn.commit()


def get_posts(query):
    conn = create_connection(f)
    x = pd.read_sql_query(query, conn)

    pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', -1)
    print(x)


def insertStats():
    sql_create_stats_table = """ CREATE TABLE IF NOT EXISTS STATS (
                                        team text,
                                        game_id integer,
                                        yards integer,
                                        points integer,
                                        passingTDs integer,
                                        rushingTDs integer,
                                        PRIMARY KEY(game_id,team),
                                        FOREIGN KEY (team) REFERENCES TEAM(School)

                                    ); """

    conn = create_connection(f)
    create_table(conn, sql_create_stats_table)

    query = "SELECT season,id FROM MATCHUP WHERE season>=2004;"
    c = conn.cursor()
    c.execute(query)
    rows = c.fetchall()

    sql = "INSERT INTO STATS (team,game_id,yards,points,passingTDs,rushingTDs) VALUES(?,?,?,?,?,?)"
    for y, id in rows:
        stats = json.loads(requests.get(base+"games/teams",
                                        params=[('year', int(y)), ('gameId', int(id))]).content)

        try:
            for t in stats[0]['teams']:
                school = t['school']
                points = t['points']
                yards = 0
                passingTDs = 0
                rushingTDs = 0
                for cat in t['stats']:
                    if cat['category'] == "totalYards":
                        yards = cat['stat']

                    if cat['category'] == 'rushingTDs':
                        rushingTDs = cat['stat']

                    if cat['category'] == 'passingTDs':
                        passingTDs = cat['stat']

                c.execute(sql, (school, id, yards, points,
                                passingTDs, rushingTDs))
                conn.commit()

        except IndexError as e:
            print(y, id)
        except sqlite3.IntegrityError as R:
            pass


def insert_teams():
    sql_create_team_table = """ CREATE TABLE IF NOT EXISTS TEAM (
                                        School text ,
                                        Conference text,

                                        Mascot text,


                                        PRIMARY KEY(School)

                                    ); """

    sql_create_roster_table = """ CREATE TABLE IF NOT EXISTS ROSTER (
                                        Name text ,
                                        Team text,
                                        Position text,



                                        PRIMARY KEY(Name,Team),
                                        FOREIGN KEY (Team) REFERENCES TEAM(School)


                                    ); """
    conn = create_connection(f)
    create_table(conn, sql_create_team_table)
    create_table(conn, sql_create_roster_table)
    sql = "INSERT INTO TEAM (School,Conference,Mascot) VALUES(?,?,?)"
    sqlroster = "INSERT INTO ROSTER (Name,Team,Position) VALUES(?,?,?)"
    cur = conn.cursor()
    conferences = json.loads(requests.get(base+"conferences").content)

    for i in conferences:
        abbv = i['abbreviation']

        if abbv in ['ACC', 'SEC', 'B1G', 'PAC', 'B12']:
            teams = requests.get(
                base+"teams", params=[('conference', abbv)]).content
            for i in json.loads(teams):

                school = i['school']
                mascot = i['mascot']
                try:
                    cur.execute(sql, (school, abbv, mascot))
                except sqlite3.IntegrityError as e:
                    pass
                conn.commit()

                roster = json.loads(requests.get(
                    base+"roster", params=[('team', school)]).content)
                for p in roster:
                    n = p['first_name']+","+p['last_name']
                    pos = p['position']
                    try:
                        cur.execute(sqlroster, (n, school, pos))
                    except sqlite3.IntegrityError as e:
                        pass
                    conn.commit()


def insertVenue():
    venues = json.loads(requests.get(base+"venues").content)
    sql_create_venue_table = """ CREATE TABLE IF NOT EXISTS VENUE (
                                        name text ,
                                        capacity integer ,
                                        location text,

                                        PRIMARY KEY(name)
                                    ); """
    conn = create_connection(f)
    create_table(conn, sql_create_venue_table)
    sql = "INSERT INTO VENUE (name,capacity,location) VALUES(?,?,?)"
    cur = conn.cursor()

    for v in venues:
        name = v['name']
        cap = v['capacity']
        loc = v['city']+","+v['state']
        try:
            cur.execute(sql, (name, cap, loc))
            conn.commit()
        except sqlite3.IntegrityError as e:
            pass


def insert_matchups(season):
    sql_create_matchup_table = """ CREATE TABLE IF NOT EXISTS MATCHUP (
                                        hometeam text ,
                                        awayteam text ,
                                        week integer,
                                        season integer,
                                        venue text,
                                        winner text,
                                        id integer,
                                        PRIMARY KEY(id),
                                        FOREIGN KEY (hometeam) REFERENCES TEAM(School),
                                        FOREIGN KEY (awayteam) REFERENCES TEAM(School),
                                        FOREIGN KEY (winner) REFERENCES TEAM(School),
                                        FOREIGN KEY (venue) REFERENCES VENUE(name)
                                    ); """

    conn = create_connection(f)
    create_table(conn, sql_create_matchup_table)
    sql = "INSERT INTO MATCHUP (hometeam,awayteam,week,season,venue,winner,id) VALUES(?,?,?,?,?,?,?)"
    cur = conn.cursor()
    conferences = json.loads(requests.get(base+"conferences").content)

    for i in conferences:
        abbv = i['abbreviation']

        if abbv in ['ACC', 'SEC', 'B1G', 'PAC', 'B12']:
            teams = requests.get(
                base+"teams", params=[('conference', abbv)]).content
            for i in json.loads(teams):

                school = i['school']

                games = requests.get(
                    base+'games', params=[('year', str(season)), ('team', school)]).content
                for g in json.loads(games):
                    # print(":".join([g['home_team'],g['away_team'], str(g['week']), str(g['season'])] ))
                    ht = g['home_team']
                    at = g['away_team']
                    week = str(g['week'])
                    season = str(g['season'])
                    venue = g['venue']
                    hp = int(g['home_points'])
                    ap = int(g['away_points'])
                    id = int(g['id'])

                    if hp > ap:
                        winner = ht
                    else:
                        winner = at

                    try:
                        cur.execute(
                            sql, (ht, at, week, season, venue, winner, id))
                        conn.commit()
                    except sqlite3.IntegrityError as e:
                        pass


def sqlstatement(val):

    conn = create_connection(f)
    cur = conn.cursor()
    try:
        cur.execute(val)
        conn.commit()
    except Exception as e:
        print("hello")


if __name__ == "__main__":

    insertVenue()
    insert_teams()

    for i in range(1990, 2019):
        insert_matchups(i)
        print("Inserted matchups for year", i)
    insertStats()
