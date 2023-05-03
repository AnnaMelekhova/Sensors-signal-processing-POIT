from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect    
import time
import random
import json
import serial
async_mode = None
import MySQLdb 
import configparser as ConfigParser
# async_mode = None

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock() 

ser = serial.Serial("/dev/ttyS0")
ser.baudrate = 9600
ser.flushInput()

shouldMonitor = False       

def background_thread(args):
    count = 0    
    dataCounter = 0
    dataList = []
    dataToSave = []
    state = False;
    global shouldMonitor
    i = 0
    while True:
        if args:
            A = dict(args).get('A')
            btnV = dict(args).get('btn_value')
            monitorBtn = dict(args).get('monitorBtnVal')
        else:
            A = 1
            btnV = 'null' 
            monitorBtn = False
          
        socketio.sleep(2)
        
        print(args)
        ###############SENSOR DATA#####################
        line = ser.readline().decode('utf-8').rstrip()
        data = json.loads(line)
        ###############SENSOR DATA#####################
        
        ###############TEST DATA######################
        #f = open('dummydata.json')
        #line = json.load(f)
        #data = line[count]
        ###############TEST DATA######################
        temp = data['temperature']
        hum = data['humidity']
        dist = data['distance']
        ir = data['ir']
        dataDict = {
             "time": count,
             "t": temp,
             "h": hum,
             "d": dist,
             "ir": ir}
        dataList.append(dataDict)
        print(shouldMonitor)
        print(state)
        print(select_from_table(5))
        if shouldMonitor or ir == 0:
            print("zapisujem")
            dataToSave.append(dataDict)
            state = True
        else:
        #if state and not shouldMonitor:
            #print("ukladam do suboru")
            #state = False
            #write_to_db(dataToSave)
            #i = i+1
            #f = open("data.txt", "a")
            #f.write("id: "+ str(i) +" - "+ json.dumps(dataToSave)+"\n")
            #f.close()
            #dataToSave = []
            
            if len(dataToSave)>0 :
                print(str(dataToSave))
                l = str(dataToSave).replace("'", "\"")
                write_to_db(l)
                print("ukladam do suboru")
                state = False
                #write_to_db(dataToSave)
                i = i+1
                f = open("data.txt", "a")
                f.write("id: "+ str(i) +" - "+ json.dumps(dataToSave)+"\n")
                f.close()
            dataToSave = []
        count +=1
        socketio.emit('my_response',
                      {'data': dataDict, 'count': count})
        
        # if(saveDataNow == True): 
            # with open("data.json", "w") as f:
                # json.dump(dataList, f)

def write_to_db(val):
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    print(val)
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM graph")
    cursor.execute("INSERT INTO graph (id, hodnoty) VALUES (%s, %s)",(0, val),)
    print('___________________________ZAPISUJEM DO DB_________________________')
    db.commit()
    
def select_from_table(idx):
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM graph where id=%s",(idx,))
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results = (dict(zip(columns, row)))
    if results == []:
        print("empty")
    else:
        data = results.get('hodnoty')
        #data = data.replace( '[', '')
        #data = data.replace( ']', '')
        data = json.loads(data)
        print(type(data))
    #print(data)
    #print(type(data))
        return data 

    
def search_and_parse(index):
	f = open("data.txt", "r")
	for line in f:
		id_str, json_str = line.strip().split(' - ',1)
		id_int = int(id_str.split(':')[1].strip())
		if id_int == index:
			data = json.loads(json_str)
			return data
	return []                      
                      

@app.route('/')
def index():
    return render_template('index.html')
    
# @app.route('/graphlive', methods=['GET', 'POST'])
# def graphlive():
    # return render_template('graphlive.html', async_mode=socketio.async_mode)
  
# @app.route('/gauge', methods=['GET', 'POST'])
# def gauge():
    # return render_template('gauge.html', async_mode=socketio.async_mode)

@socketio.on('my_event')
def test_message(message):  
	if(message['value'] == ""): 
		return
	response = search_and_parse(int(message['value']))
	emit('file_response',
         {'data': response})

@socketio.on('db_event')
def testdb_message(message):  
	if(message['value'] == ""): 
		return
	response = select_from_table(int(message['value']))
	print(response)
	emit('DB_response',
         {'data': response})

@socketio.on('disconnect_request')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event')
def db_message(message):   
    session['btn_value'] = message['value']  
    
    
@socketio.on('monitoringButton')
def handle_message(data):
    global shouldMonitor
    if data['status'] == 'true':
        print('Monitoring button is on')
        shouldMonitor = True
        print(shouldMonitor)
    elif data['status'] == 'false':
        print('Monitoring button is off')
        shouldMonitor = False
	

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
