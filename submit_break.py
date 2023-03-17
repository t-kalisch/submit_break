
import streamlit as st
from common_functions import *
import datetime
from datetime import date
import pandas as pd
st.set_page_config(page_title="Submit break",page_icon="coffee",layout="wide")


#--------------------------------------- submit a complete coffee break ----------------------------------------------
def submit_break(persons,coffees,date_br):					# submitting break into database
	db = init_connection()
	cursor = db.cursor(buffered=True)
	names = get_members()
	
	persons_comp=[]
	coffees_comp=[]
	persons_str = ""
	coffees_str = ""
	valid_break = False
	for i in range(len(persons)):
		if coffees[i] != "" and persons[i] != "":
			persons_comp.append(persons[i])
			coffees_comp.append(coffees[i])
			valid_break = True
	if valid_break == False:
		st.error("No valid break")
	else:
		if date_br[0] == "" and date_br[1] == "" and date_br[2] == "":
			date_br[0] = datetime.date.today().day
			date_br[1] = datetime.date.today().month
			date_br[2] = datetime.date.today().year
		else:
			date_str=date_br[0]+"-"+date_br[1]+"-"+date_br[2]+" 0:00"
			if(datetime.datetime.now() < datetime.datetime.strptime(date_str, "%d-%m-%Y %H:%M")):
				st.error("Invalid date entered!")
				return
		id_ext = str(date_br[2])
		if int(date_br[1]) < 10:
			id_ext += "0"
		id_ext += str(int(date_br[1]))
		if int(date_br[0]) < 10:
			id_ext += "0"
		id_ext += str(int(date_br[0]))
		
		cursor.execute("SELECT id_ext FROM breaks WHERE id_ext like '"+id_ext+"%'")    #searching for breaks of the same day as enterd break
		ids=cursor.fetchall()

		if len(ids) == 0:
			id_ext += "01"
		else:
			id_ext = str(int(ids[len(ids)-1][0])+1)

		cursor.execute("insert into breaks (id_ext, day, month, year) values (%s, %s, %s, %s)", (id_ext, date_br[0], date_br[1], date_br[2]))
		cursor.execute("insert into break_sizes (id_ext, size) values (%s, %s)", (id_ext, len(persons_comp)))
		for i in range(len(persons_comp)):
			
			cursor.execute("select count(*) from members where name = '"+persons_comp[i]+"'")
			tmp = cursor.fetchone()
			if tmp[0] == 0:
				cursor.execute("insert into members (name,admin) values ('"+str(persons_comp[i].upper())+"',0)")                                             #adding person to members table
				cursor.execute("alter table holidays add "+persons_comp[i].upper()+" int")                                                    #adding person to holidays table
				cursor.execute("create table if not exists mbr_"+persons_comp[i].upper()+" (id_ext char(10), n_coffees int, primary key(id_ext), CONSTRAINT fk_member_"+persons_comp[i].upper()+"_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")     #creating a table for each individual person
				cursor.execute("alter table exp_values add "+persons_comp[i]+" varchar(4)")
				cursor.execute("update exp_values set "+persons_comp[i]+" = '0.0'")
				cursor.execute("alter table exp_values_dev add "+persons_comp[i]+" varchar(5)")
				cursor.execute("update exp_values_dev set "+persons_comp[i]+" = '0.0'")
				cursor.execute("alter table exp_values_stdev add "+persons_comp[i]+" varchar(4)")
				cursor.execute("update exp_values_stdev set "+persons_comp[i]+" = '0.0'")
				db.commit()
				update_database()
				st.success(persons_comp[i].upper()+" was successfully included into the database.")
			if i == 0:
				persons_str += persons_comp[i].upper()
				coffees_str += coffees_comp[i]
			else:
				persons_str += "-"
				coffees_str += "-"
				persons_str += persons_comp[i].upper()
				coffees_str += coffees_comp[i]
			cursor.execute("insert into mbr_"+persons_comp[i].upper()+" (id_ext, n_coffees) values (%s, %s)", (id_ext, coffees_comp[i]))
		cursor.execute("insert into drinkers (id_ext, persons, coffees) values (%s, %s, %s)", (id_ext, persons_str, coffees_str))
		st.success("Your coffee break has been saved (Persons: "+persons_str+", Coffees: "+coffees_str+")")
	db.commit()
	db.close
				
		

#------------------------------- check whether break ID was entered or not
def add_coffee_to_break_check(id_ext, coffee_name, logged_in_user):
    if id_ext=="":
        id_ext = last_breaks[len(last_breaks)-1][0]
    add_coffee_to_break(id_ext, coffee_name, logged_in_user)		

#---------------------------------- add coffee to existing coffee break ---------------------------------------------------
def add_coffee_to_break(id_ext, name, user):
	db = init_connection()
	cursor = db.cursor(buffered=True)
	names = get_members()
	if name == "":
		name = user
	cursor.execute("select persons, coffees from drinkers where id_ext = '"+id_ext+"'")
	#st.write(cursor.fetchall())
	drinker_data=list(cursor.fetchall()[0])
	if drinker_data == []:
		st.warning("Invalid extended ID")
		return
	else:
		user_exists = False
		for i in range(len(names)):
			if name.upper() == names[i]:
				user_exists = True
				cursor.execute("select n_coffees from mbr_"+name.upper()+" where id_ext = '"+id_ext+"'")
				tmp = cursor.fetchall()
				if tmp == []:
					cursor.execute("insert into mbr_"+name.upper()+" (id_ext, n_coffees) values (%s, %s)", (id_ext, 1))
					drinker_data[0] = str(drinker_data[0])+"-"+name.upper()
					drinker_data[1] = str(drinker_data[1])+"-1"
					
					cursor.execute("select size from break_sizes where id_ext = '"+id_ext+"'")
					tmp1 = cursor.fetchall()
					cursor.execute("update break_sizes set size = "+str(int(tmp1[0][0])+1)+" where id_ext = '"+id_ext+"'")
					
					cursor.execute("update drinkers set persons = '"+drinker_data[0]+"', coffees = '"+drinker_data[1]+"' where id_ext = '"+id_ext+"'")
					st.success("Added "+name.upper()+" into break "+id_ext+".")
				else:
					cursor.execute("update mbr_"+name.upper()+" set n_coffees = "+str(tmp[0][0]+1)+" where id_ext = '"+id_ext+"'")
					persons = drinker_data[0].split("-")
					coffees = drinker_data[1].split("-")
					for j in range(len(persons)):
						if persons[j] == name:
							coffees[j] = int(coffees[j]) + 1
						if j == 0:
							coffees_str = str(coffees[j])
						else:
							coffees_str = coffees_str+"-"+str(coffees[j])

					cursor.execute("update drinkers set persons = '"+drinker_data[0]+"', coffees = '"+coffees_str+"' where id_ext = '"+id_ext+"'")
					st.success("Added a coffee for "+name.upper()+" into break "+id_ext+".")
		if user_exists == False:
			cursor.execute("insert into members (name,admin) values ('"+name.upper()+"',0)")                                             #adding person to members table
			cursor.execute("alter table holidays add "+name.upper()+" int")                                                    #adding person to holidays table
			cursor.execute("create table if not exists mbr_"+name.upper()+" (id_ext char(10), n_coffees int, primary key(id_ext), CONSTRAINT fk_member_"+name.upper()+"_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")     #creating a table for each individual person
			cursor.execute("insert into mbr_"+name.upper()+" (id_ext, n_coffees) values (%s, %s)", (id_ext, 1))
			db.commit()
			update_database()
			st.success(persons_comp[i].upper()+" was successfully included into the database.")
			cursor.execute("select size from break_sizes where id_ext = '"+id_ext+"'")
			tmp1 = cursor.fetchall()
			cursor.execute("update break_sizes set size = "+str(int(tmp1[0][0])+1)+" where id_ext = '"+id_ext+"'")
			drinker_data[0][0] = drinker_data[0][1]+"-"+name.upper()
			drinker_data[0][1] = drinker_data[0][1]+"-1"
			cursor.execute("update drinkers set persons = '"+drinker_data[0][0]+"', coffees = '"+drinker_data[0][1]+"' where id_ext = '"+id_ext+"'")
			st.success("Added "+name.upper()+" to the database and into break "+id_ext+".")
	db.commit()
	db.close()



########################################################################################################################################################################
#####################################################    MAIN    #######################################################################################################
########################################################################################################################################################################
st.subheader("**:coffee:** Submit a coffee break")
#if 'logged_in' not in st.session_state or 'user_name' not in st.session_state or 'admin' not in st.session_state or 'attempt' not in st.session_state:
#    st.warning("Warning! Your session was terminated due to inactivity. Please return to home to restart it and regain access to all features.")
#else:

#if st.session_state.admin != "1":
#  st.warning("You do not have the permission to submit a coffee or break. Please contact a system administrator for further information.")
#
#elif st.session_state.admin == "1":

st.markdown("Please enter the names and number of coffees for the break.")
col1,col2,col3,col4,col5,col6,col7,col8, col9 = st.columns([1,1,1,1,1,1,1,1,1])
p1_name = col7.text_input("Person 1")
p2_name = col8.text_input("Person 2")
p3_name = col9.text_input("Person 3")
col1,col2,col3,col4,col5,col6,col7,col8, col9 = st.columns([1,1,1,1,1,1,1,1,1])
tk = col1.text_input("TK")
pb = col2.text_input("PB")
db = col3.text_input("DB")
flg = col4.text_input("FLG")
shk = col5.text_input("SHK")
sb = col6.text_input("SB")
p1_coffees = col7.text_input("Coffees 1")
p2_coffees = col8.text_input("Coffees 2")
p3_coffees = col9.text_input("Coffees 3")
col1,col2,col3,col4,col5,col6,col7,col8, col9 = st.columns([1,1,1,1,1,1,1,1,1])
date_day = col1.text_input("Day", placeholder = datetime.date.today().day)
date_month = col2.text_input("Month", placeholder = datetime.date.today().month)
date_year = col3.text_input("Year", placeholder = datetime.date.today().year)
persons=['TK','PB','DB','FLG','SHK','SB',p1_name,p2_name,p3_name]
coffees=[tk,pb,db,flg,shk,sb,p1_coffees,p2_coffees,p3_coffees]
date_br=[date_day,date_month,date_year]
col1,col2 = st.columns([2,6])
col1.button("Submit break", on_click=submit_break, args=(persons,coffees,date_br))
st.write("-" * 34)
st.write("Enter an extended ID and Name to add a coffee to a break.")
last_breaks=get_last_breaks(10)
col1, col2, col3 = st.columns([1,1,3])
id_ext = col1.text_input("Extended ID", placeholder=last_breaks[len(last_breaks)-1][0])
coffee_name = col2.text_input("Username", placeholder="User")
col1.button("Add coffee", on_click=add_coffee_to_break_check, args=(id_ext, coffee_name, st.session_state.user_name))
df=pd.DataFrame(last_breaks,columns=['Extended ID','Date','Drinkers','Coffees'])
col3.markdown("Last 10 breaks")
col3.dataframe(df, width=600, height=400)

	
	
#------- footer ----------------
footer="""<style>
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color:  grey;
text-align: center;
fontsize: 10 pt;
}
</style>
<div class="footer">
<p>Developed by P. C. Brehm and T. Kalisch. Web design by T. Kalisch <a style='display: block; text-align: center</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
