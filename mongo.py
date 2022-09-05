#Connecting with cluster
import pymongo
client_cloud = pymongo.MongoClient("mongodb+srv://Rahul:Rahul@cluster0.0dl2gmk.mongodb.net/?retryWrites=true&w=majority")
client_cloud

#creating a database for lms

lms_db = client_cloud["lms"]

#creating collections

collection_name = "emp_leave_balance"
emp_leave_balance = lms_db[collection_name]

collection_name = "emp_man_table"
emp_man_table = lms_db[collection_name]

collection_name = "employee"
employee = lms_db[collection_name]

collection_name = "employee_details"
employee_details = lms_db[collection_name]

collection_name = "holidays_list"
holidays_list = lms_db[collection_name]

collection_name = "leave_status"
leave_status = lms_db[collection_name]

collection_name = "lu_leave"
lu_leave = lms_db[collection_name]

