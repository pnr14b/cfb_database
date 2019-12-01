import requests
import json
import sqlite3
from sqlite3 import Error
import pandas as pd

base = "http://api.collegefootballdata.com/"
f = r"cfb_db"


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


def get_posts(conn, query):
    x = pd.read_sql_query(query, conn)

    pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', -1)
    print(x)


# """ def insertVenue():
#     venues = json.loads(requests.get(base+"venues").content)
#     sql_create_venue_table = """ CREATE TABLE IF NOT EXISTS VENUE(
#     name text,
#     capacity integer,
#     location text,

#     PRIMARY KEY(name, location)
# )
# """
#     conn = create_connection(f)
#     create_table(conn, sql_create_venue_table)
#     sql = "INSERT INTO VENUE (name,capacity,location) VALUES(?,?,?)"
#     cur = conn.cursor()

#     for v in venues:
#         name = v['name']
#         cap = v['capacity']
#         loc = v['city']+","+v['state']
#         try:
#             cur.execute(sql, (name, cap, loc))
#         except sqlite3.IntegrityError as e:
#             pass
#         conn.commit()
#     get_posts(conn, "SELECT * FROM VENUE") """


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

    get_posts(conn, "SELECT * FROM TEAM;")
    get_posts(conn, "SELECT * FROM ROSTER;")

    # games = requests.get(base+'games',params=[('year',str(season)),('team',school)]).content
    # for g in json.loads(games):
    # print(":".join([g['home_team'],g['away_team'], str(g['week']), str(g['season'])] ))
    #       insert(conn,g['home_team'],g['away_team'],str(g['week']),str(g['season']))


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

    get_posts(conn, "SELECT * FROM VENUE")


def insert_matchups(season):
    sql_create_matchup_table = """ CREATE TABLE IF NOT EXISTS MATCHUP (
                                        hometeam text ,
                                        awayteam text ,
                                        week integer,
                                        season integer,
                                        venue text,
                                        winner text,
                                        PRIMARY KEY(hometeam,awayteam,week,season),
                                        FOREIGN KEY (hometeam) REFERENCES TEAM(School),
                                        FOREIGN KEY (awayteam) REFERENCES TEAM(School),
                                        FOREIGN KEY (winner) REFERENCES TEAM(School),
                                        FOREIGN KEY (venue) REFERENCES VENUE(name)
                                    ); """

    conn = create_connection(f)
    create_table(conn, sql_create_matchup_table)
    sql = "INSERT INTO MATCHUP (hometeam,awayteam,week,season,venue,winner) VALUES(?,?,?,?,?,?)"
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
                    if hp > ap:
                        winner = ht
                    else:
                        winner = at

                    try:
                        cur.execute(sql, (ht, at, week, season, venue, winner))
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

    for i in range(2000, 2019):
        insert_matchups(i)
    # get_posts(create_connection(file),"SELECT * FROM MATCHUP;")
    # for i in range(2000,2010):
    #   insertgames(conn,i)

    # get_posts(conn)
    create_connection(f).close()
