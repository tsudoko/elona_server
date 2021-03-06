# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Response
from contextlib import closing
from datetime import datetime
import codecs

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

DATABASE = '/home/ruin0x11/elona.db'

def connect_to_database():
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        date = int(datetime.now().strftime("%s"))
        for i in range(0,10):
            db.execute('insert into chat (time, kind, text, addr) values (?, ?, ?, ?)',
                     [int(date), 1, "弱気ものprinは猫に殺された「なむ」", "127.0.0.1"])
            db.execute('insert into vote (name, votes, addr, time, totalvotes) values (?, ?, ?, ?, ?)',
                     ["弱気ものprin" + str(i), 100 - i, '127.0.0.1', date, 1000])
        db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def chat_type_from_num(x):
    return {
        0: 'chat',
        1: 'dead',
        2: 'wish',
    }.get(x, 0)

def chat_type_from_string(x):
    return {
        'chat': 0,
        'dead': 1,
        'wish': 2,
    }.get(x, 0)

@app.route("/text.txt", methods=["GET"])
def text():
    response = "<!--START-->\n%\n素敵な異名コンテスト♪1  [１ヶ月で自動リセット]%\nYour favorite alias♪1  [Auto reset every month]%"
    return Response(str.encode(response, "shift-jis"), mimetype='text/plain')


@app.route("/log.txt", methods=["GET"])
def get_log():
    response = ""
    first = query_db('select * from chat order by id desc limit 1', one=True)
    no = first['id']+1 if first else 1
    response += str(no) + "<C>\n<!--START-->\n"
    for line in query_db('select * from chat order by id desc limit 30'):
        date = datetime.fromtimestamp(line['time']).strftime("%m/%d(%I)")
        response += str(line['id']) + '%' + date + '%' + chat_type_from_num(line['kind']) + line['text'] + '%' + line['addr'] + '%\n'
    response += "<!--END-->\n<!-- WebTalk v1.6 --><center><small><a href='http://www.kent-web.com/' target='_top'>WebTalk</a></small></center>"
    return Response(str.encode(response, "shift-jis"), mimetype='text/plain')
    

@app.route("/vote.txt", methods=["GET"])
def get_vote():
    response = ""
    first = query_db('select * from chat order by id desc limit 1', one=True)
    i = 1
    no = first['id']+1 if first else 1
    for line in query_db('select * from vote limit 100'):
        date = datetime.fromtimestamp(line['time']).strftime("%s")
        response += str(i) + '<>' + line['name'] + '<>' + str(line['votes']) + '<>' + line['addr'] + '<>' + date + '#' + str(line['totalvotes']) + '#' + '1' + '#<>\n'
        i += 1
    return Response(response, mimetype='text/plain')


@app.route("/cgi-bin/wtalk/wtalk2.cgi", methods=["GET"])
def add_chat():
    db = get_db()

    mode = request.args.get('mode')
    comment = request.args.get('comment')
    print(repr(comment.decode('shift-jis').encode('utf-8'), file=sys.stderr))
    #chat_type = chat_type_from_string(commentstr[:5])
    #text = commentstr[5:-11]
    #time = int(datetime.now().strftime("%s"))
    #addr = request.remote_addr

    #db.execute('insert into chat (time, kind, text, addr) values (?, ?, ?, ?)',
    #                [time, chat_type, text, addr])
    #db.commit()
    return get_log()

@app.route("/cgi-bin/vote/votec.cgi", methods=["GET"])
def add_vote():
    db = get_db()

    no = request.args.get('no')
    mode = request.args.get('mode')
    vote = codecs.decode(request.args.get('vote'), 'unicode_escape')
    #votestr = str.encode(vote, "latin-1").decode("shift-jis")[:-11]
    votestr = vote
    addr = request.remote_addr
    time = int(datetime.now().strftime("%s"))
    if mode == 'wri':
        first = query_db('select * from vote where name = ?', [votestr], one=True)
        if first:
            return get_vote()
        db.execute('insert into vote (name, votes, addr, time, totalvotes) values (?, ?, ?, ?, ?)',
                        [votestr, 0, addr, time, 0])
        db.commit()
    return get_vote()

if __name__ == "__main__":
    app.run()
