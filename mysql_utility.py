import config
import mysql.connector


def mysql_connection():
    '''
    A utility funtion in terms to get the connection and cursor object.
    :return: connection object , cursor object
    '''
    try:
        temp_cox = mysql.connector.connect(host=config.config['MYSQL_DATABASE_HOST'],
                                           port=config.config['MYSQL_DATABASE_PORT'],
                                           database=config.config['MYSQL_DATABASE_DB'],
                                           user=config.config['MYSQL_DATABASE_USER'],
                                           password=config.config['MYSQL_DATABASE_PASSWORD']
                                           )
        temp_curr = temp_cox.cursor(dictionary=True)
        return temp_cox, temp_curr
    except mysql.connector.Error as err:
        print(err)


def select_query(query):
    '''
    :param query: Accept as string type query. Function doesn't check the authenticity of the query.
    :return: return the result in form of dictionary
    '''
    try:
        con, cursor = mysql_connection()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        con.close()
        return result
    except mysql.connector.Error as err:
        print(err)

# print(type(select_query("SELECT * FROM `emp_leave_balance`")),(select_query("SELECT * FROM `emp_leave_balance`")))
# users = select_query("SELECT `EMP_ID` FROM `employee_details`;")
# user = [user[j] for user in users for j in user]
