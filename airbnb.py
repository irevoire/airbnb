from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

app.config['SERVER_NAME'] = '127.0.0.1:5000'

app.url_for('static', filename='index.html')

#connection to PGRSQL database
postgre_sql = psycopg2.connect("dbname=airbnb user=postgres password=postgres")
#creation of cursor to execute SQL commands
cur = postgre_sql.cursor()

#creation of the announcements table
cur.execute("""
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL UNIQUE PRIMARY KEY, 
    title VARCHAR(500) NOT NULL, 
    image VARCHAR(2000) NOT NULL, 
    description VARCHAR(100000) NOT NULL, 
    lon int NOT NULL, 
    lat int NOT NULL
);
""")

@app.route("/")
def root():
    return app.send_static_file('index.html')

@app.route("/lair", methods=['GET'])
def look_for_lair():
    args = request.args
    print(args)
    query_request = "SELECT id, title, image, lon, lat FROM announcements WHERE lat > {lat1} AND lat < {lat2} AND lon > {lng1} AND lon < {lng2}".format(lat1=args['lat1'], lat2=args['lat2'], lng1=args['lng1'], lng2=args['lng2'])
    print(query_request)
    if args.get('search') is not None:
        query_request = query_request + " AND title LIKE '{search}'".format(search=args['search'])
    cur.execute(query_request)

    return jsonify(cur.fetchall())

@app.route("/lair/<id>", methods=['GET'])
def one_lair(id):
    cur.execute("SELECT * from announcements WHERE id = %s", (id))
    return jsonify(cur.fetchone())

@app.route("/lair", methods=['POST'])
def new_form():   
    content = request.json
    print(content)
    cur.execute("""
    INSERT INTO announcements (title, image, description, lon, lat) 
    VALUES (%s, %s, %s, %s, %s)
    """, (content['title'], content['image'], content['description'], content['lon'], content['lat']))
    return jsonify({"status":"success"})

@app.route("/lair/<id>", methods=['DELETE'])
def delete_form(id):  
    cur.execute("DELETE FROM announcements WHERE id = %s", (id))
    return jsonify({"status":"success"}) 

@app.route("/debug", methods=['GET'])
def debug():
    cur.execute("SELECT * FROM announcements")
    return jsonify(cur.fetchall())

app.run()