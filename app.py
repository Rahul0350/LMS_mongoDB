from flask import (Flask, render_template, request, redirect, jsonify, session)
import config
import mysql_utility
import arrow
import bcrypt
import mongo
import json
from bson import json_util

app = Flask(__name__)
app.secret_key = "helloomniwyse"


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route('/getLeaveTypeAndCount')
def getLeaveTypeAndCount():
    try:
        conn = mongo.lms_db
        leave_details = conn.lu_leave.find()
        return json.loads(json_util.dumps(leave_details))
    except Exception as e:
        print(e)


@app.route('/getEmpLeaveStatus/<int:emp_id>')
def getEmpLeaveStatus(emp_id):
    try:
        conn = mongo.lms_db
        EmpLeaveStatus = conn.leave_status.find({'EMP_ID': emp_id})
        return json.loads(json_util.dumps(EmpLeaveStatus))
    except Exception as e:
        print(e)


@app.route('/getEmpLeaveBalance/<int:emp_id>')
def getEmpLeaveBalance(emp_id):
    try:
        conn = mongo.lms_db
        EmpLeaveBalance = conn.emp_leave_balance.find({'EMP_ID': emp_id})
        return json.loads(json_util.dumps(EmpLeaveBalance))
    except Exception as e:
        print(e)
        return showMessage()


@app.route('/updatePublicHoliday', methods=['PUT'])
def updatePublicHoliday():
    try:
        json_data = request.json
        h_name = json_data['HOLIDAY_NAME']
        h_date = json_data['HOLIDAY_DATE']
        h_is_optional = json_data['IS_OPTIONAL']
        h_is_active = json_data['IS_ACTIVE']
        h_year = json_data['YEAR']
        conn = mongo.lms_db
        conn.holidays_list.update_one(
            {'YEAR': h_year, 'HOLIDAY_NAME': h_name},
            {"$set": {
                'HOLIDAY_DATE': h_date,
                'IS_OPTIONAL': h_is_optional,
                'IS_ACTIVE': h_is_active
            }}
        )
        respone = jsonify('Holiday updated successfully!')
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
        return showMessage()


@app.route('/createPublicHoliday', methods=['POST'])
def createPublicHoliday():
    json_data = request.json
    h_name = json_data['HOLIDAY_NAME']
    h_date = json_data['HOLIDAY_DATE']
    h_is_optional = json_data['IS_OPTIONAL']
    h_is_active = json_data['IS_ACTIVE']
    h_year = json_data['YEAR']
    try:
        conn = mongo.lms_db
        conn.holidays_list.insert_one(
            {'HOLIDAY_NAME': h_name, 'HOLIDAY_DATE': h_date, 'IS_OPTIONAL': h_is_optional, 'IS_ACTIVE': h_is_active,
             'YEAR': h_year})
        respone = jsonify('Holiday added successfully!')
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
        return showMessage()


@app.route('/getManLeaveRequests/<man_id>', methods=['GET'])
def getManLeaveRequests(man_id):
    try:
        conn = mongo.lms_db
        ManLeaveRequests = conn.emp_man_table.find({'MAN_ID': int(man_id)})
        return json.loads(json_util.dumps(ManLeaveRequests))

    except Exception as e:
        print(e)
        return 'Bad Request'


@app.route('/applyLeaveRequest', methods=['POST'])
def applyLeaveRequest():
    try:
        json_data = request.json
        leave_id = json_data['leave_ID']
        emp_id = json_data['EMP_ID']
        leave_type_id = json_data['LAEAVE_TYPE_ID']
        start_date = json_data['START_DATE']
        end_date = json_data['END_DATE']
        applied_date = json_data['APPLIED_DATE']
        approved_manager_id = json_data['APPROVED_MANAGER_ID']
        conn = mongo.lms_db
        conn.leave_status.insert_one(
            {'leave_ID': leave_id, 'EMP_ID': emp_id, 'LAEAVE_TYPE_ID': leave_type_id, 'START_DATE': start_date,
             'END_DATE': end_date,
             'APPLIED_DATE': applied_date, 'APPROVED_MANAGER_ID': approved_manager_id})
        respone = jsonify('Leave Applied successfully!')
        respone.status_code = 200
    except Exception as e:
        print(e)
        return showMessage()
    return respone


# To get all details of the all employees
@app.route('/getEmployeesDetails')
def getEmployeesDetails():
    try:
        conn = mongo.lms_db
        emp_details = conn.employee_details.find()
        return json.loads(json_util.dumps(emp_details))
    except Exception as e:
        print(e)
        return showMessage()


# To get all the Employee under particular manager
@app.route('/getEmployessUnderManager/<string:mng_id>')
def getEmployessUnderManager(mng_id):
    try:
        conn = mongo.lms_db
        EmployessUnderManager = conn.employee_details.find({'MAN_ID': int(mng_id)})
        return json.loads(json_util.dumps(EmployessUnderManager))

    except Exception as e:
        print(e)
        return showMessage()


# To get all the Employee with approved manager id and status is pending
@app.route('/approvedManagerIdAndPending/<string:man_id>')
def approvedManagerIdAndPending(man_id):
    try:
        conn = mongo.lms_db
        approvedManagerIdAndPending = conn.leave_status.find({'APPROVED_MANAGER_ID': int(man_id), 'STATUS': 'PENDING'})
        return json.loads(json_util.dumps(approvedManagerIdAndPending))

    except Exception as e:
        print(e)
        return showMessage()


@app.route('/getUserCategory/<int:emp_id>')
def getUserCategory(emp_id):
    try:
        conn = mongo.lms_db
        getUserCategory = conn.employee_details.find({'EMP_ID': emp_id},
                                                     {'EMP_ID': 1, 'EMP_FNAME': 1, 'EMP_LNAME': 1, 'IS_MAN': 1})
        return json.loads(json_util.dumps(getUserCategory))
    except:
        return 'Bad Credentials'


@app.route('/updateLeaveStatus/<emp_id>/<leave_id>', methods=['PUT'])
def updateLeaveStatus(emp_id, leave_id):
    ujson = request.json
    manager = False
    emp = [emp_id]
    status = ujson['status']
    leave = [emp_id, leave_id]
    try:
        conn = mongo.lms_db
        con, cur = mysql_utility.mysql_connection()
        cur.execute('SELECT ls.leave_id, ed.is_man '
                    'FROM lms.leave_status AS ls '
                    'JOIN  lms.employee_details AS ed '
                    'ON ls.emp_id=ed.emp_id '
                    'WHERE ed.emp_id=%s', emp)
        managerResult = cur.fetchall()
        cur.close()
        con.close()
        if managerResult[0]['is_man'] == 1:
            manager = True
        if manager:
            con, cur = mysql_utility.mysql_connection()
            checkTemp = False
            cur.execute('SELECT ls.leave_id, ls.status, ed.emp_id, ls.laeave_type_id, ls.start_date, ls.end_date '
                        'FROM lms.leave_status AS ls '
                        'JOIN  lms.employee_details AS ed '
                        'ON ls.emp_id=ed.emp_id '
                        'WHERE ed.man_id=%s', emp)
            leaveManager = cur.fetchall()
            for i in leaveManager:
                if i['leave_id'] == int(leave_id):
                    checkTemp = True
                    status = i['status']
                    leaveEmpId = [i['emp_id']]
                    leaveTypeId = [i['laeave_type_id'], leave_id]
                    startDate = arrow.get(str(i['start_date']))
                    endDate = arrow.get(str(i['end_date']))
                    delta = (endDate - startDate)
            cur.close()
            con.close()
            con, cur = mysql_utility.mysql_connection()
            if checkTemp and status == 'PENDING':
                if status.upper() == 'REVOKE':
                    cur.execute("UPDATE leave_status SET status='REVOKE',approved_manager_id=%s WHERE leave_id=%s",
                                leave)
                    con.commit()
                elif status.upper() == 'ACCEPT':
                    cur.execute('SELECT elb.LAEAVE_TYPE_ID,elb.LAEAVE_COUNT '
                                'FROM lms.leave_status AS ls '
                                'JOIN lms.emp_leave_balance AS elb '
                                'ON ls.EMP_ID=elb.EMP_ID '
                                'WHERE elb.LAEAVE_TYPE_ID=%s and ls.leave_id=%s', leaveTypeId)
                    leaveValue = cur.fetchone()
                    if leaveValue['LAEAVE_COUNT'] >= (delta.days + 1):
                        cur.execute("UPDATE leave_status SET status='ACCEPT',approved_manager_id=%s WHERE leave_id=%s",
                                    leave)
                        con.commit()
                        putValue = leaveValue['LAEAVE_COUNT'] - delta.days - 1
                        passVale = [putValue, leaveEmpId[0], leaveTypeId[0]]
                        cur.execute(
                            'UPDATE emp_leave_balance SET laeave_count=%s WHERE emp_id=%s AND laeave_type_id=%s',
                            passVale)
                        con.commit()
                    else:
                        cur.execute("UPDATE leave_status SET status='REVOKE',approved_manager_id=%s WHERE leave_id=%s",
                                    leave)
                        con.commit()
                else:
                    return 'Please update the correct status'
            else:
                return 'Please pass correct leave id or leave is approved or revoked'
        else:
            con, cur = mysql_utility.mysql_connection()
            checkTemp = False
            for i in managerResult:
                if i['leave_id'] == int(leave_id):
                    checkTemp = True
                    break
            if checkTemp and status == 'PENDING':
                if status.upper() == 'REVOKE':
                    cur.execute("UPDATE leave_status SET status='REVOKE' WHERE leave_id=%s", leave)
                    con.commit()
                else:
                    return 'Please update the correct status'
            else:
                return 'Please enter your leave id or your leave is approved'
        cur.close()
        con.close()
        response = jsonify('Leave Status updated')
        response.status_code = 200
        return response
    except:
        return showMessage()


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return jsonify({'message': 'Unauthorized'})
    else:
        try:
            conn = mongo.lms_db
            data = request.json
            EMP_ID = data.get('EMP_ID')
            EMP_FNAME = data.get('EMP_FNAME')
            EMP_MNAME = data.get('EMP_MNAME')
            EMP_LNAME = data.get('EMP_LNAME')
            IS_MAN = data.get('IS_MAN')
            MAN_ID = data.get('MAN_ID')
            EMP_CONTACT_NO = data.get('EMP_CONTACT_NO')
            EMP_PASSWORD = data.get('EMP_PASSWORD').encode('utf-8')
            hash_password = bcrypt.hashpw(EMP_PASSWORD, bcrypt.gensalt())
            conn.employee_details.insert_one(
                {'EMP_ID': EMP_ID, 'EMP_FNAME': EMP_FNAME, 'EMP_MNAME': EMP_MNAME, 'EMP_LNAME': EMP_LNAME,
                 'IS_MAN': IS_MAN,
                 'MAN_ID': MAN_ID, 'EMP_CONTACT_NO': EMP_CONTACT_NO, 'EMP_PASSWORD': hash_password})
            return jsonify({'message': 'You are registered successfully'})

        except Exception as e:
            print(e)
            return showMessage()


@app.route('/login', methods=["GET", "POST"])
def login():
    conn = mongo.lms_db
    if request.method == 'POST':
        EMP_ID = request.json['EMP_ID']
        EMP_FNAME = request.json['EMP_FNAME']
        EMP_PASSWORD = request.json['EMP_PASSWORD'].encode('utf-8')
        Emp = conn.employee_details.find_one({'EMP_ID': EMP_ID})
        if len(Emp) > 0:
            print(Emp["EMP_PASSWORD"])
            # print(Emp["EMP_PASSWORD"].encode('utf-8'))
            if bcrypt.hashpw(EMP_PASSWORD, Emp["EMP_PASSWORD"]) == Emp["EMP_PASSWORD"]:
                session['EMP_ID'] = Emp['EMP_ID']
                session['EMP_FNAME']  = Emp['EMP_FNAME']
                return jsonify({'message': 'You are logged in successfully'})
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return jsonify({'message': 'Bad Request - invalid credendtials'})


@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'You successfully logged out'})


@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone


if __name__ == '__main__':
    app.run(port=config.PORT, host=config.HOSTNAME, debug=config.DEBUG)
