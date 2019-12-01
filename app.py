from flask import Flask, render_template, request, send_from_directory
import requests
import json
import sqlite3
from sqlite3 import Error
import pandas as pd

f = r"cfb_db"
app = Flask(__name__)
app.config['JS'] = "static/js"
app.config['FAVICON'] = "static"


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    conn.row_factory = sqlite3.Row
    return conn.cursor()


def get_posts(conn, query):
    x = pd.read_sql_query(query, conn)

    pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', -1)
    print(x)


@app.route('/matchup', methods=['GET'])
def getMatchup():
    team1 = request.args.get('Team1')
    team2 = request.args.get('Team2')
    year1 = request.args.get('year1')
    year2 = request.args.get('year2')

    if not team2:
        conn = create_connection(f)
        query = "SELECT * FROM MATCHUP WHERE ((hometeam = ? ) OR (awayteam = ?) ) AND (season >= ? AND season <= ?) ORDER BY season,week  "
        conn.execute(query, (team1, team1, year1, year2))
        rows = conn.fetchall()
        return json.dumps([dict(ix) for ix in rows])

    conn = create_connection(f)
    query = "SELECT * FROM MATCHUP WHERE ((hometeam = ? AND awayteam = ?) OR (hometeam = ? AND awayteam = ?) ) AND (season >= ? AND season <= ?) ORDER BY season,week  "
    conn.execute(query, (team1, team2, team2, team1, year1, year2))
    rows = conn.fetchall()
    return json.dumps([dict(ix) for ix in rows])


@app.route('/teams', methods=['GET'])
def getTeams():
    opt_param = request.args.get("conf")
    if opt_param is None:
        return render_template("teams.html")

    conn = create_connection(f)
    query = "SELECT * FROM TEAM WHERE Conference = ?  "
    conn.execute(query, (opt_param,))
    rows = conn.fetchall()
    return json.dumps([dict(ix) for ix in rows])


@app.route('/roster', methods=['GET'])
def getRoster():
    team = request.args.get("team")
    if team is None:
        return render_template("roster.html")

    pos = request.args.get('pos')

    conn = create_connection(f)
    if team and not pos:
        query = "SELECT Name,Position FROM ROSTER WHERE Team = ?"
        conn.execute(query, (team,))
        rows = conn.fetchall()
        return json.dumps([dict(ix) for ix in rows])
    if team and pos:
        query = "SELECT Name,Position FROM ROSTER WHERE Team = ? AND Position = ? ORDER BY Position"
        conn.execute(query, (team, pos,))
        rows = conn.fetchall()
        return json.dumps([dict(ix) for ix in rows])


@app.route('/venue', methods=['GET'])
def getMbyV():

    venue = request.args.get('venue')
    if not venue:
        return render_template('venue.html')
    year1 = request.args.get('year1')
    year2 = request.args.get('year2')
    conn = create_connection(f)
    query = "SELECT * FROM MATCHUP WHERE venue = ? AND season >= ? AND season<= ? "
    conn.execute(query, (venue, year1, year2,))
    rows = conn.fetchall()
    return json.dumps([dict(ix) for ix in rows])


@app.route('/conference_matchups', methods=['GET'])
def conference_matchups():
    c1 = request.args.get('c1')
    c2 = request.args.get('c2')
    s = request.args.get('season')
    if not c1:
        return render_template("confmatchups.html")

    conn = create_connection(f)
    query = """
    SELECT MATCHUP.hometeam,MATCHUP.awayteam,MATCHUP.winner,MATCHUP.season 
    FROM MATCHUP 
    WHERE season = ? AND 
    (
        (   hometeam IN (SELECT School FROM TEAM WHERE Conference = ?) AND 
            awayteam IN (SELECT School FROM TEAM WHERE Conference = ?)  
        ) 
        OR 
        (   
             hometeam IN (SELECT School FROM TEAM WHERE Conference = ?)  AND 
             awayteam IN (SELECT School FROM TEAM WHERE Conference = ?)  
        ) 
    ) 
    """
    conn.execute(query, (s, c1, c2, c2, c1))
    rows = conn.fetchall()
    return json.dumps([dict(ix) for ix in rows])


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/js/<path:path>', methods=["GET"])
def get_send_js(path):
    return send_from_directory(app.config['JS'], path)


if __name__ == "__main__":

    #print(getMatchup("Florida State", "Florida", 2001, 2003))
    #print(getRoster("Florida State", "QB"))
    #print(getMbyV('Bobby Bowden Field at Doak Campbell Stadium', 2001, 2008))

    app.run(debug=True)
