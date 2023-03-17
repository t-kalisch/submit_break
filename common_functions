import streamlit as st
import mysql.connector as mysql
import paramiko
from paramiko import SSHClient
import datetime
from datetime import date

#---------------------------------------- initiates connection to database -----------------------------------------
#@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
def init_connection():
    return mysql.connect(**st.secrets["mysql"])

#---------------------------------------- initiates connection to ssh server -----------------------------------------
#@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
#def init_connection_ssh():
#	ssh = paramiko.SSHClient()
#	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#	return ssh.connect(**st.secrets["ssh-server"])

 

#----------------------------------------- getting all members from database ---------------------------------------
#@st.cache
def get_members():
    db = init_connection()
    cursor = db.cursor(buffered=True)

    names=[]

    cursor.execute("select name from members")              #getting all members tables
    mbrs=cursor.fetchall()
    mbrs=list(mbrs)
    for i in range(len(mbrs)):
        names.append(mbrs[i][0])
    db.close()
    return names

#------------------------------------ getting guest password from database ------------------------------------
def get_guest_pw():
	db = init_connection()
	cursor = db.cursor(buffered=True)
	cursor.execute("select guest_pw from update_status")
	pw=cursor.fetchall()[0][0]
	db.close()
	return pw

#------------------------------------ getting all user data ------------------------------------------
def get_user_data():
	db = init_connection()
	cursor = db.cursor(buffered=True)
	cursor.execute("select name, password, admin from members")
	user_data=cursor.fetchall()
	db.close()
	return user_data

#----------------------------------- getting simple data ------------------------------------------
def get_simple_data():							# getting simple data from database
	db = init_connection()
	cursor = db.cursor(buffered=True)
	cursor.execute("select value from simple_data")
	simple_data=cursor.fetchall()

	db.close()
	return simple_data

#----------------------------- getting last 10 breaks from database ---------------------------------
#@st.cache
def get_last_breaks(last_break):
	db = init_connection()
	cursor = db.cursor(buffered=True)
	cursor.execute("select * from breaks order by id_ext desc limit "+str(last_break))
	breaks=cursor.fetchall()
	cursor.execute("select * from drinkers order by id_ext desc limit "+str(last_break))
	drinkers=cursor.fetchall()

	last_breaks=[]
	for i in range(len(breaks)):
		temp=[]
		date=str(breaks[len(breaks)-i-1][2])+"."+str(breaks[len(breaks)-i-1][3])+"."+str(breaks[len(breaks)-i-1][4])
		temp.append(breaks[len(breaks)-i-1][1])
		temp.append(date)
		temp.append(drinkers[len(drinkers)-i-1][2])
		temp.append(drinkers[len(drinkers)-i-1][3])
		last_breaks.append(temp)
	db.close()
	return last_breaks


#----------------------------- getting all months from start date to now ---------------------------------
#@st.cache
def get_months(first_date):
    db = init_connection()
    cursor = db.cursor(buffered=True)
    
    month_info=[]
    months=[]
    month_id=[]

    #cursor.execute("SELECT max(id_ext) FROM breaks")        #getting month names from beginning to current
    #temp=cursor.fetchone()
    #temp=list(temp)

    #last_date=datetime.date(int(temp[0][0:4]),int(temp[0][4:6]),int(temp[0][6:8]))
    last_date = datetime.date.today()
    for month in months_between(first_date,last_date):
    #for i in range(months_between(first_date,last_date)):
        if(month.month<10):
            month_id.append(str(month.year)+"0"+str(month.month))
        else:
            month_id.append(str(month.year)+str(month.month))
        months.append(month.strftime("%B")[0:3]+" '"+month.strftime("%Y")[2:4])
    month_info.append(months)
    month_info.append(month_id)
    
    db.close()
    return month_info
    

def months_between(start_date, end_date):                   #method to get months between two dates
    if start_date > end_date:
        raise ValueError(f"Start date {start_date} is not before end date {end_date}")
    else:
        year = start_date.year
        month = start_date.month
	
        #counter=0
        while (year, month) <= (end_date.year, end_date.month):
            yield datetime.date(year, month, 1)
            # Move to the next month.  If we're at the end of the year, wrap around
            # to the start of the next.
            #
            # Example: Nov 2017
            #       -> Dec 2017 (month += 1)
            #       -> Jan 2018 (end of year, month = 1, year += 1)
            #
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            #counter += 1
    #return counter


#----------------------- manually updating database ----------------------------
def update_database():
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(**st.secrets["ssh-server"])
	
	
	stdin, stdout, stderr = ssh.exec_command("cd mysql_scripts; ./simple_update.sh")
	lines = stdout.readlines()
	ssh.close()
