
import sqlite3
import os
path = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(path+'\hospital.db',check_same_thread=False)
cur = con.cursor()






def contains(id,typ):
    if typ == 'doc':
        data = cur.execute('select * from Doctorlogin where email =(?)',(id,))
    else:
        data = cur.execute('select * from patientlogin where email =(?)',(id,))
    if data.fetchall():
        return True
    return False
    
def check_auth(id,pswd,typ):
    if typ == 'doc':
        data = cur.execute('select * from Doctorlogin where email =(?) and password =(?)',(id,pswd))
    else:
        data = cur.execute('select * from patientlogin where email =(?) and password =(?)',(id,pswd))

    if data.fetchall():
        return True
    return False
def check_doc(email):
    data = cur.execute('select * from Doctorlogin where email =(?)',(email,))
    return data.fetchone()

def get_doc_details(email):
        data = cur.execute('select * from doctor where email =(?)',(email,))
        return data.fetchone()
def get_doc_with_id(id):
    data = cur.execute('select * from doctor where id =(?)',(id,))
    return data.fetchone()

def get_appointments(doc,spc):
    data = cur.execute('select * from appointments where doctor=(?) and speciality=(?) ',(doc,spc))
    return data.fetchall()

def spc_apts(id):
    data = cur.execute('select * from appointments where patient_id= (?)',(id,))
    return data.fetchall()

def all_docs():
    data = cur.execute('select name,speciality,email,experiance,age,phonenumber,id,schedule from doctor')
    return data.fetchall()

def all_patients():
    data = cur.execute("select * from patient")
    return data.fetchall()

def all_inpatients():
    data = cur.execute("select * from inpatient")
    return data.fetchall()


def all_appointments():
    data =  cur.execute("select * from appointments")
    return data.fetchall()
def get_patient_details(email):
        data = cur.execute('select * from patient where email =(?) ',(email,))
        return data.fetchone()
def get_patient_withid(id):
        data = cur.execute('select * from patient where id =(?) ',(id,))
        return data.fetchone()

def check_patient(email):
    data = cur.execute('select * from patientlogin where email =(?)',(email,))
    return data.fetchone()

def add_appointments(spc,doc_name,typ,diag,pname,phn,gen,email,docID,date,age,patient_id):
    query = cur.execute("""insert into appointments ('doctor','speciality','type','patientname','symptoms','phonenumber','gender',patient_email,doctorId,appointment_date,age,patient_id) values (?,?,?,?,?,?,?,?,?,?,?,?)""",(doc_name,spc,typ,pname,diag,phn,gen,email,docID,date,age,patient_id))
    con.commit()

def register_patient(req,file,typ):
    
    query = cur.execute("""insert into patient ('email','Name','gender','age','phonenumber','img','type') values (?,?,?,?,?,?,?) """,(req['email'],req['name'],req['gender'],req['age'],req['phnum'],file,typ))
    con.commit()
def register_patient_details(req,typ):
    query = cur.execute("""insert into patient ('email','Name','gender','age','phonenumber','type') values (?,?,?,?,?,?) """,(req['email'],req['name'],req['gender'],req['age'],req['phnum'],typ))
    con.commit()
def register_inpatient(name,diag,prep,docid,doc_name,spc,ad_date,f,patient_id):
    query = cur.execute("""insert into inpatient ('Name','diagnosis','prescription','doctorId','doctor-name','speciality','admision-date','report','patient_id') values (?,?,?,?,?,?,?,?,?)""",(name,diag,prep,docid,doc_name,spc,ad_date,f,patient_id))
    con.commit()
    


def patient_login_update(req):
    query = cur.execute("""insert into patientlogin ('email','password') values (?,?)""",(req['email'],req['password']))
    con.commit()

def admin_add_doctor_login(req):
    query = cur.execute("""insert into Doctorlogin ('email','password') values (?,?)""",(req['email'],req['password']))
    con.commit()

def admin_add_doctor_details(req,img):
    query = cur.execute("""insert into doctor ("name","speciality","img","email","experiance","age","phonenumber","schedule") values (?,?,?,?,?,?,?,?) """,(req['name'],req['speciality'],img,req['email'],req['exp'],req['age'],req['phnum'],req['schedule']))
    con.commit()

def patient_appointments(email):
    data = cur.execute('select * from appointments where patient_email =(?)',(email,))
    return data.fetchone()


def prescription_update(data):
    query = cur.execute("""UPDATE appointments SET prescription =(?) ,diagnosis=(?)  WHERE id = (?) """,(data['prescription'],data['diagnosis'],data['id']))
    con.commit()

def get_inpatient(docid):
    data = cur.execute('select * from inpatient where doctorId=(?)',(docid,))
    return data.fetchall()