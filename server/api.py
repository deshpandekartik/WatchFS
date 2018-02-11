from flask import Flask
import time
from flask import request
from flask import Response
app = Flask(__name__)
from sqlite_database import *
from flask import render_template

response_success_status = "0"	# 0 - returns on success
response_failure_status = "1" 	# 1 - return on failure


# Database, key value store to store data
DATAMAP = {}		# Main database, maintains read write operation data , mapped to PCName
BLACKLISTEDFILES = [] 	# list of mallicious files

# database object
sqlite = sqlite_database()
# initialize database
sqlite.initialize()

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)

@app.route('/API/initialize', methods=['GET', 'POST'])
def api_initialize():
	print request.json
	
	data = request.json
	NodeID = data.get("nodeid")
	
	if NodeID is None :
		return Response(response_failure_status, status=502, mimetype='application/json')	
	
        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/read', methods=['GET', 'POST'])
def api_read():
	print request.json

	return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/create' , methods=['GET', 'POST'])
def api_create():
        print request.json
	

	data = request.json
        NodeID = data.get("nodeid")
	path = data.get("path")
	mode = data.get("mode")
	uid = data.get("uid")
	gid = data.get("gid")
	timestamp = int(time.time())
	size = 0

	if path.endswith('swp') or path.endswith('swk') or path.endswith('svk'):
		return Response(response_failure_status, status=502, mimetype='application/json')

        if NodeID is None or path is None or mode is None or uid is None or gid is None:
                return Response(response_failure_status, status=502, mimetype='application/json')


	if path in BLACKLISTEDFILES:
		textualdata = "Anomaly detected ! A Blacklisted file named " + path + " was created"
		string = "insert into notification (nodeid, textualdata) values('" + str(NodeID) + "','" + str(textualdata) + "')"
                sqlite.execute_query(string)	

	lite = sqlite.get_row_count("select * from datamap where nodeid = '" + NodeID + "' and path = '" + path + "'")
	count = len(lite)

	if count == 0 :
		string = "insert into datamap (nodeid, path, mode, uid, gid, size,timestamp) values('" + str(NodeID) + "','" + str(path) + "','" + str(mode) + "','" + str(uid) + "','" + str(gid) + "','" + str(size) + "','" + str(timestamp) + "')"

		sqlite.execute_query(string)	

	# maintain extension count
	if "." in path:
		fileextension = path.split(".")[1]
	else:
		fileextension = "-"

	if fileextension == "" or fileextension is None:
		fileextension = "-"
	
	print fileextension	
	lite = sqlite.get_row_count("select * from extensioncount where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")
        count = len(lite)

        if count == 0 :
                string = "insert into extensioncount (nodeid, extension, count) values('" + str(NodeID) + "','" + str(fileextension) + "','" + str(0) + "')"
                sqlite.execute_query(string)
	else:
		sizesql = sqlite.fetch_data("select count from extensioncount where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")
		sizesql = int(sizesql) + 1	
		sqlite.execute_query("update extensioncount set count = '" + str(sizesql) + "' where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")

	return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/write' , methods=['GET', 'POST'])
def api_write():
        print request.json

        data = request.json
        NodeID = data.get("nodeid")
        path = data.get("path")
        size = data.get("size")
	timestamp = str(int(time.time()))
	
	if path.endswith('swp') or path.endswith('swk') or path.endswith('svk'):
                return Response(response_failure_status, status=502, mimetype='application/json')

        if NodeID is None or path is None or size is None:
                return Response(response_failure_status, status=502, mimetype='application/json')

	sizesql = sqlite.fetch_data("select size from datamap where nodeid = '" + NodeID + "' and path = '" + path + "'")
	print sizesql

	size = int(sizesql) + int(size)
	sqlite.execute_query("update datamap set size = '" + str(size) + "' where nodeid = '" + NodeID + "' and path = '" + path + "'")

        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/truncate' , methods=['GET', 'POST'])
def api_truncate():
        print request.json

        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/open', methods=['GET', 'POST'])
def api_open():
	print request.json

	return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/chown', methods=['GET', 'POST'])
def api_chown():
        print request.json

        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/chmod', methods=['GET', 'POST'])
def api_chmod():
        print request.json

        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/rename', methods=['GET', 'POST'])
def api_rename():
        print request.json

	data = request.json
        NodeID = data.get("nodeid")
        old = data.get("old")
        new = data.get("new")

        if NodeID is None or old is None or new is None:
                return Response(response_failure_status, status=502, mimetype='application/json')

        sqlite.execute_query("update datamap set path = '" + str(new) + "' where nodeid = '" + NodeID + "' and path = '" + old + "'")

	if "." in old:
                oldfileextension = old.split(".")[1]
        else:
                oldfileextension = "-"

	if "." in new:
                newfileextension = new.split(".")[1]
        else:
                newfileextension = "-"

	sqlite.execute_query("update extensioncount set extension = '" + str(newfileextension) + "' where nodeid = '" + NodeID + "' and extension = '" + str(oldfileextension) + "'")


	path = new

	# maintain extension count
        if "." in path:
                fileextension = path.split(".")[1]
        else:
                fileextension = "-"

        if fileextension == "" or fileextension is None:
                fileextension = "-"

        lite = sqlite.get_row_count("select * from extensioncount where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")
        count = len(lite)

        if count == 0 :
                string = "insert into extensioncount (nodeid, extension, count) values('" + str(NodeID) + "','" + str(fileextension) + "','" + str(0) + "')"
                sqlite.execute_query(string)
        else:
                sizesql = sqlite.fetch_data("select count from extensioncount where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")
                sizesql = int(sizesql) + 1
                sqlite.execute_query("update extensioncount set count = '" + str(sizesql) + "' where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")


        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/mkdir', methods=['GET', 'POST'])
def api_mkdir():
        print request.json

        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/rmdir', methods=['GET', 'POST'])
def api_rmdir():
        print request.json

        return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/API/unlink', methods=['GET', 'POST'])
def api_unlink():
        print request.json	
	
	data = request.json
        NodeID = data.get("nodeid")
        path = data.get("path")

	sqlite.execute_query("delete from datamap where nodeid = '" + NodeID + "' and path = '" + path + "'")
	
        # maintain extension count
        if "." in path:
                fileextension = path.split(".")[1]
        else:
                fileextension = "-"

        if fileextension == "" or fileextension is None:
                fileextension = "-"

        lite = sqlite.get_row_count("select * from extensioncount where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")
        count = len(lite)

        if count == 0 :
                string = "insert into extensioncount (nodeid, extension, count) values('" + str(NodeID) + "','" + str(fileextension) + "','" + str(0) + "')"
                sqlite.execute_query(string)
        else:
                sizesql = sqlite.fetch_data("select count from extensioncount where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")
                sizesql = int(sizesql) - 1
                sqlite.execute_query("update extensioncount set count = '" + str(sizesql) + "' where nodeid = '" + NodeID + "' and extension = '" + fileextension + "'")

        return Response(response_success_status, status=200, mimetype='application/json')



@app.route('/JSON/open_data', methods=['GET', 'POST'])
def json_open():
	print request.json

	return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/JSON/read_data', methods=['GET', 'POST'])
def json_read():
	print request.json

	return Response(response_success_status, status=200, mimetype='application/json')

@app.route('/JSON/create_data', methods=['GET', 'POST'])
def json_create():
	print request.json

	return Response(response_success_status, status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
