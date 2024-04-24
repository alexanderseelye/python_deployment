# Filename - server.py

# Imports
from flask import Flask, json, request, Response #Flask imports for data sending/receiving
from flask_headers import headers
from flask_cors import CORS
import psycopg #Library for manipulating the postgresql database
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
 


# Initializing flask app
app = Flask(__name__)
CORS(app)

# USER = "postgres"
# PASSWD = "postgres"
# DB = "projectdata"
# HOST = "localhost"

USER = "eecs447groupproject"
PASSWD = "Qwertyuiop1!"
DB = "cloudprojectdata"
HOST = "databaseproject.postgres.database.azure.com"

my_headers = {
    "Access-Control-Allow-Origin" : "*",
    "Content-Type" : "application/json"
}
 
db_conn = psycopg.connect(f"dbname={DB} user={USER} password={PASSWD} host={HOST}")
db_cur = db_conn.cursor()

user_db_conn = None
user_db_cur = None

def changeSession(user, passwd, con, cur):
    cur.close()
    con.close()
    new_con = psycopg.connect(f"dbname={DB} user={user} password={passwd} host={HOST}")    
    print(new_con.cursor().execute("SELECT SESSION_USER"))
    return new_con



#teamArr is list of string names for teams
#statsNameArr is a list of string names for the stats
#stats2DArr is a 2d list of values for each of the corresponding stats in the statsNameArr
#returns a graph image

def visualize_data(teamArr, statsNameArr, stats2DArr):
    # plt.ioff()
    mpl.use("Agg")
    # measure the length of the passed in lists
    teamLen = len(teamArr)
    nameLen = len(statsNameArr)
    statsLen = len(stats2DArr)

    # declare some constants
    multiplier = 0

    # What x is equivalent to depends on the value of statsLen
    if statsLen < 3:
        width = .5
        x = np.arange(0, teamLen)

    elif statsLen < 5:
        width = .3
        x = np.arange(0, teamLen * 1.5, 1.5)

    elif statsLen < 8:
        width = .25
        x = np.arange(0, teamLen * 2, 2)

    fig, ax = plt.subplots(figsize=(5, 5))

    for i in range(statsLen):
        # iterate through the 2D array making a subplot with each
        offset = width * multiplier
        barPiece = ax.bar(x + offset, stats2DArr[i], width, label=statsNameArr[i])
        multiplier += 1

    ax.set_title("Comparison Statistics by Team")
    ax.legend(loc="upper right", fontsize="small")
    ax.set_xticks(x + width, teamArr)

    ax.set_ylim(0, np.max(stats2DArr) * 1.5)

    plt.savefig("../frontend/my_app/src/graphs/bargraph.png")

#teamArr is list of string names for teams
#statsNameArr is a list of string names for the stats
#stats2DArr is a 2d list of values for each of the corresponding stats in the statsNameArr
#returns a graph image

def visualize_heatmap(teamArr, statsNameArr, stats2DArr):

    # Constant length values of the different input arrays
    teamLen = len(teamArr)
    nameLen = len(statsNameArr)
    statsLen = len(stats2DArr)

    # Create
    ax = plt.gca()

    # create heat map on data with specified color (cmap argument)
    im = ax.imshow(stats2DArr, cmap="viridis")

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(ylabel="Statistics", rotation=-90, va="bottom")

    ax.set_xticks(np.arange(stats2DArr.shape[1]), labels=teamArr)
    ax.set_yticks(np.arange(stats2DArr.shape[0]), labels=statsNameArr)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                    labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
                rotation_mode="anchor")

    # Gets rid of grid lines
    ax.spines[:].set_visible(False)

    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    for i in range(nameLen):
        for j in range(teamLen):
            text = ax.text(j, i, stats2DArr[i, j],
                        ha="center", va="center", color="white")

    plt.savefig("../frontend/my_app/src/graphs/heatmap.png")



#Route for seeing a data

@app.route('/users')
@headers(my_headers)
def get_users():
    db_cur.execute("SELECT * FROM users")
    x = db_cur.fetchall()
    #print(x)
    y = {
        "columns": ["ID", "Username", "Password"],
        "results": x
        }
    print(json.dumps(y))
    # Returning an api for showing in  reactjs
    return json.dumps(y)



@app.route("/players", methods=['GET', 'POST'])
@headers(my_headers)
def get_players():
    data = request.json
    db_cur.execute(data.get("command"))
    x = db_cur.fetchall()
    #print(x)
    y = {
        "columns": ["Name", "Points", "Rebounds", "Assists", "Games Played", "PFP"],
        "results": x
        }
    # print(db_cur.execute("SELECT SESSION_USER, CURRENT_USER").fetchall())
    return json.dumps(y)



@app.route("/login", methods=['GET', 'POST'])
@headers(my_headers)
def login():
    print("Login Attempt")
    data = request.json
    user = data.get("user")
    passwd = data.get("password")
    # print(user)
    # print(passwd)
    success = False
    for record in db_cur.execute("SELECT * FROM users").fetchall():
        if user in record and passwd in record:
            success = True
            break

    # if success:
    #     # db_cur.execute(f"SET SESSION AUTHORIZATION {user}")
    #     # db_conn.commit()
    #     user_db_conn = changeSession(user, passwd, db_conn, db_cur)
    #     user_db_cur = user_db_conn.cursor()
    #     # print(user_db_cur.execute("SELECT SESSION_USER"))

    return json.dumps({"login": success})



@app.route("/register", methods=['GET', 'POST'])
@headers(my_headers)
def register():
    data = request.json
    print(data.get("user"))
    print(data.get("password"))
    newuser = data.get("user")
    newpass = data.get("password")
    
    already_exists = False
    success = False
    for record in db_cur.execute("SELECT * FROM users").fetchall():
        if newuser in record:
            already_exists = True
            break
    if not (already_exists):
        print("Inserting new user: " + newuser)
        db_cur.execute(f"INSERT INTO users (username, passwd) VALUES ('{newuser}', '{newpass}')")
        db_cur.execute(f"""CREATE ROLE {newuser} WITH
                            LOGIN
                            CREATEDB
                            CREATEROLE
                            NOINHERIT
                            NOREPLICATION
                            CONNECTION LIMIT -1
                            PASSWORD '{newpass}';""")
        db_conn.commit()
        success = True

    return json.dumps({"login": success})



@app.route("/stats", methods=['GET', 'POST'])
@headers(my_headers)
def stats():
    data = request.json
    command = data.get("command")
    # print(command)
    stats_query_template = command
    success = False
    statstoquery = ["fg_percent", "three_percent", "two_percent", "ft_percent"]
    db_cur.execute(data.get("command"))
    teamabbr = db_cur.fetchall()
    print(teamabbr)

    for i in range(len(teamabbr)):
        temp = str(teamabbr[i]).replace(",", "")
        temp2 = ""
        for j in temp:
            if (j == "(" or j == ")" or j == "'"):
                    continue
            temp2 += j
        teamabbr[i] = temp2

    statnames = ["FG%", "3%", "2%", "FT%"]
    unprocessedstatsarray = []
    # processedstatsarray = []
    # to_replace = "teamabbr"

    for stat in statstoquery:
        unprocessedstatsarray.append(db_cur.execute(command.replace("teamabbr", stat, 1)).fetchall())
        # to_replace = stat
        #  unprocessedstatsarray.append(db_cur.execute(f"SELECT {stat} FROM teamstats WHERE season = 2024 ORDER BY id ASC").fetchall())

    # print(unprocessedstatsarray)

    for i in range(len(unprocessedstatsarray)):
        # temp = []
        for j in range(len(unprocessedstatsarray[i])):
            temp = str(unprocessedstatsarray[i][j]).replace(",", "")
            temp2 = ""
            for k in temp:
                if (k == "(" or k == ")"):
                    continue
                temp2 += k
            unprocessedstatsarray[i][j] = float(temp2)

    data = np.array(unprocessedstatsarray)
    
    visualize_data(teamabbr, statnames, data)
    visualize_heatmap(teamabbr, statnames, data)

    success = True
    return json.dumps({"login": success})



@app.route("/getteams")
@headers(my_headers)
def getTeams():
    teamdata = db_cur.execute("SELECT teamname, teamabbr FROM teamstats WHERE season = 2024").fetchall()

    return json.dumps(teamdata)


@app.route("/geteasternconference")
@headers(my_headers)
def getEasternConference():
    db_cur.execute("SELECT teamname FROM easternconference WHERE season = 2024")
    data = db_cur.fetchall()

    return json.dumps({
        "teams": data
    })

# # Running app
# if __name__ == '__main__':
#     app.run(debug=True)