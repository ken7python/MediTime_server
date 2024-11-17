from flask import Flask, request
from flask_cors import CORS
import sqlite3
import json

dbname = 'data.db'
conn = sqlite3.connect(dbname,check_same_thread=False)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx] 
    return d


conn.row_factory = dict_factory

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/')
def index():
    return 'メディタイム'

@app.route('/hukuyouTime',methods=['POST','GET'])
def hukuyouTime():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        cur = conn.cursor()
        
        valid = data['valid']
        weekBool = data['weekBool']
        label = data['label']
        
        if (valid):
            valid_int = 1
        else:
            valid_int = 0
        
        if weekBool:
            weekBool_int = 1
        else:
            weekBool_int = 0
        cur.execute("UPDATE valid SET hukuyouTime=?,WeekdaySchedule=? WHERE label=?",(valid_int,weekBool_int,label))
        if (valid):
            schedule = data['schedule']
        
            print(schedule)
            cur.execute("UPDATE hukuyouTime SET Sunday=?,Monday=?,Tuesday=?,Wednesday=?,Thursday=?,Friday=?,Saturday=? WHERE label=?",(schedule["sunday"],schedule["monday"],schedule["tuesday"],schedule["wednesday"],schedule["thursday"],schedule["friday"],schedule["saturday"],label))
        conn.commit()
        cur.close()
        return '更新しました'
    if request.method == 'GET':
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM valid")
        valid = cur.fetchall()
        cur.execute("SELECT * FROM hukuyouTime")
        hukuyouTime = cur.fetchall()
        
        print(valid)
        print(hukuyouTime)
        cur.close()
        return {'valid':valid,'hukuyouTime':hukuyouTime}
#服用履歴
@app.route('/hukuyou',methods=['POST','GET'])
def hukuyou():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        date = data['date']
        label = data['label']
        day_of_week = data['day_of_week']
        cur = conn.cursor()
        
        this_type="label"
        
        cur.execute("SELECT * FROM hukuyouHistory WHERE date=? AND label=? AND day_of_week=? AND type=?",(date,label,day_of_week,this_type))
        sameData = cur.fetchall()
        if sameData:
            print("すでに登録されています")
            return "すでに登録されています"
        else:
            print("登録します")
            cur.execute("INSERT INTO hukuyouHistory(date,label,day_of_week,type) VALUES(?,?,?,?)",(date,label,day_of_week,this_type))
            conn.commit()
        cur.close()
        return "OK"
    if request.method == 'GET':
        cur = conn.cursor()
        cur.execute("SELECT * FROM hukuyouHistory")
        hukuyouHistory = cur.fetchall()
        cur.close()
        return {'hukuyouHistory':hukuyouHistory}
    
@app.route('/hukuyou_multiple',methods=['POST','GET'])
def hukuyou_multiple():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print("/hukuyou_multiple")
        print(data)
        date = data['date']
        labels = data['labels']
        day_of_week = data['day_of_week']
        cur = conn.cursor()
        
        this_type="label"
        
        for label in labels:
            cur.execute("SELECT * FROM hukuyouHistory WHERE date=? AND label=? AND day_of_week=? AND type=?",(date,label,day_of_week,this_type))
            sameData = cur.fetchall()
            if sameData:
                print("すでに登録されています")
            else:
                print("登録します")
                cur.execute("INSERT INTO hukuyouHistory(date,label,day_of_week,type) VALUES(?,?,?,?)",(date,label,day_of_week,this_type))
        conn.commit()
        cur.close()
        return "OK"    
#服用履歴のメモ
@app.route('/memo',methods=['POST'])
def memo():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        date = data['date']
        label = data['label']
        day_of_week = data['day_of_week']
        cur = conn.cursor()
        
        this_type="memo"
        print("/memo")
        cur.execute("INSERT INTO hukuyouHistory(date,label,day_of_week,type) VALUES(?,?,?,?)",(date,label,day_of_week,this_type))
        conn.commit()
        cur.close()
        return "OK"
@app.route('/edit_memo',methods=['POST'])
def edit_memo():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        edit_id = data['id']
        value = data['value']
        cur = conn.cursor()
        print("/edit_memo")
        if (value == ""):
            cur.execute(f"DELETE FROM hukuyouHistory WHERE id={edit_id}")
        else:
            cur.execute("UPDATE hukuyouHistory SET label=? WHERE id=?",(value,edit_id))
        conn.commit()
        cur.close()
        return "OK"
@app.route('/delete_label',methods=['POST'])
def delete_label():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        id = data["id"]
        cur = conn.cursor()
        cur.execute(f"DELETE FROM hukuyouHistory WHERE id={id}")
        conn.commit()
        cur.close()
        return "OK"
#通院履歴ラベル
@app.route('/visiting',methods=['POST','GET'])
def visiting():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        date = data['date']
        label = "✔️"
        day_of_week = data['day_of_week']
        cur = conn.cursor()
        
        this_type="label"
        
        cur.execute("SELECT * FROM visitingHistory WHERE date=? AND day_of_week=? AND type=?",(date,day_of_week,this_type))
        sameData = cur.fetchall()
        if sameData:
            print("すでに登録されています")
            return "すでに登録されています"
        else:
            print("登録します")
            cur.execute("INSERT INTO visitingHistory(date,label,day_of_week,type) VALUES(?,?,?,?)",(date,label,day_of_week,this_type))
            conn.commit()
        cur.close()
        return "OK"
    if request.method == 'GET':
        cur = conn.cursor()
        cur.execute("SELECT * FROM visitingHistory")
        hukuyouHistory = cur.fetchall()
        cur.close()
        return {'visitingHistory':hukuyouHistory}
    
#通院履歴メモ
@app.route('/visiting_memo',methods=['POST'])
def visiting_memo():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        date = data['date']
        label = data['label']
        day_of_week = data['day_of_week']
        cur = conn.cursor()
        
        this_type="memo"
        print("/memo")
        cur.execute("INSERT INTO visitingHistory(date,label,day_of_week,type) VALUES(?,?,?,?)",(date,label,day_of_week,this_type))
        conn.commit()
        cur.close()
        return "OK"
@app.route('/edit_visiting_memo',methods=['POST'])
def edit_visiting_memo():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        edit_id = data['id']
        value = data['value']
        cur = conn.cursor()
        print("/edit_memo")
        if (value == ""):
            cur.execute(f"DELETE FROM visitingHistory WHERE id={edit_id}")
        else:
            cur.execute("UPDATE visitingHistory SET label=? WHERE id=?",(value,edit_id))
        conn.commit()
        cur.close()
        return "OK"
@app.route('/delete_visiting_label',methods=['POST'])
def delete_visiting_label():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        id = data["id"]
        cur = conn.cursor()
        cur.execute(f"DELETE FROM visitingHistory WHERE id={id}")
        conn.commit()
        cur.close()
        return "OK"
@app.route('/uploadImage',methods=['POST'])
def uploadImage():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        #print(data)
        label = data['label']
        image = data['image']

        cur = conn.cursor()
        cur.execute("SELECT * FROM image WHERE label=?", (label,))
        existing_image = cur.fetchone()
        if existing_image:
            cur.execute("UPDATE image SET image=? WHERE label=?",(image,label))
            conn.commit()
            cur.close()
            return "OK"
        else:
            cur.execute("INSERT INTO image(label,image) VALUES(?,?)",(label,image))
            conn.commit()
            cur.close()
            return "OK"
@app.route('/getImage',methods=['GET'])
def getImage():
    if request.method == 'GET':
        cur = conn.cursor()
        cur.execute("SELECT * FROM image")
        image = cur.fetchall()
        cur.close()
        return {'image':image}
@app.route('/deleteImage',methods=['POST'])
def deleteImage():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        print(data)
        label = data['label']
        cur = conn.cursor()
        cur.execute("DELETE FROM image WHERE label=?",(label,))
        conn.commit()
        cur.close()
        return "OK"
    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=3000,debug=False)