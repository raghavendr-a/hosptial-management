

from logging import exception
from os import name
import re
import flask
from flask import url_for,request,session,render_template,redirect,jsonify
import flask_login
from database import *
from base64 import b64encode
app = flask.Flask(__name__)
import datetime
app.secret_key = 'hospital'
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(flask_login.UserMixin):
   pass

@login_manager.user_loader
def user_loader(email):
    
    if contains(email,'doc') or  contains(email,'p'):
        user = User()
        user.id = email
        return user
    return None 

@app.route('/')
def home():

    return render_template('home.html')

# @app.route('/<name>')
# def page_name(name):
#     return render_template('doctors/'+ name)

## Login routes
@app.route('/doctorslogin',methods=['POST'])
def doctors_login():
    email = request.form['id']
    pswd = request.form['password']
    if contains(email,'doc'):
        if check_auth(email,pswd,'doc'):
            user = User()
            
            session["id"] = email 
            user.id = email
            user.email = email
            flask_login.login_user(user)

            
            return redirect(url_for('dashboard'))
    return '<h1>incorrect details</h1>'

@app.route('/logout')
def logout():
    session["id"]  = None
    flask_login.logout_user()
    return render_template('home.html')

@app.route('/patient-login')
def check_patient_login():
    if session['id']:
        return redirect(url_for('patient_dashboard'))
    return render_template('patient/patient.html')
@app.route('/patientlogin',methods=['POST'])
def patient_login():
    email = request.form['id']
    pswd = request.form['password']
    if contains(email,'p'):
        if check_auth(email,pswd,'p'): 
            user = User() 
            patient = check_patient(email)
            session["name"] =  patient[2]
            session['id'] = email
            session['patient_id'] = patient[0]
            user.id = email
            user.email = email
            print(session)
            flask_login.login_user(user)
            return redirect(url_for('patient_dashboard'))
    return '<h1>incorrect details</h1>'


 ## Doctor routes
@app.route('/Myappointments')
@flask_login.login_required
def doctor_view_appointment():
    doc = get_doc_details(session['id'])
    aprts = get_appointments(doc[1],doc[2])
    return render_template('doctors/doctor_view_appointment.html',doc=doc,bs=b64encode,appointments=aprts)

@app.route('/doctor-login')

def check_doctor_login():
    if session['id']:
        return redirect(url_for('dashboard'))
    return render_template('doctors/doctors.html')

@app.route('/<name>')
def all_routes(name):
    patient = get_patient_details(session['id'])
    if str(name).startswith('patient'):
        return render_template('/patient/'+ name,patient=patient)
    if str(name).startswith('doctor'):
        return render_template('/doctors/'+ name)
    else:
         return render_template('/admin/'+ name)
    

@app.route('/doctor-dashboard')
@flask_login.login_required
def dashboard():
    doc = get_doc_details(session['id'])
    
    aprts = get_appointments(doc[1],doc[2])
    inpatient = get_inpatient(doc[0])
    return  render_template('doctors/doctor_dashboard.html',appointments=aprts,doc=doc,appointmentcount = len(aprts),inpatientcount=len(inpatient),inpatient=inpatient,bs=b64encode)


@app.route('/doctor-view-inpatient')
def doctor_view_inpatient():
    doc = get_doc_details(session['id'])
    inpatient = get_inpatient(doc[0])
    return render_template('doctors/doctor_view_inpatient.html',doc=doc,bs=b64encode,inpatient=inpatient)

# Patient Routes

@app.route('/patient-dashboard')
@flask_login.login_required
def patient_dashboard():
    patient = get_patient_details(session['id'])
    apts = patient_appointments(session['id'])
    
    if apts:
        doc = get_doc_with_id(apts[11])
       
        return render_template('patient/patient_dashboard.html',doc=doc,patient=patient,apt=apts,bs=b64encode)
    return render_template('patient/patient_dashboard.html',doc=None,patient=patient,bs=b64encode)

@app.route('/add-appointment',methods=['POST'])
@flask_login.login_required
def add_appointment():
    spc,doc,docId = request.form['doctor'].split('<SEP>')
    diagnosis = request.form['diagnosis']
    p = get_patient_details(session['id'])
    
    apt_date = datetime.datetime.now()
    add_appointments(doc,spc,'Out-Patient',diagnosis,p[2],p[5],p[3],session['id'],docId,apt_date,p[4],p[0])
    return redirect(url_for('book_appointment'))

@app.route('/patient-book-appointment')
@flask_login.login_required
def book_appointment():
    docs = all_docs()
   
    patient = get_patient_details(session['id'])
    return render_template('/patient/patient_book_appointment.html',docs=docs,patient=patient)

@app.route('/patient-appointments')
def allmyapts():
    patient = get_patient_details(session['id'])
    apts = spc_apts(session['patient_id'])
    return render_template('patient/patient_view_appointment.html',apts=apts,patient=patient)
@app.route('/patient-registration')

def patient_registration():
    return render_template('patient/patient_registration.html')

@app.route('/create_patient_account',methods=['POST'])

def create_patient_account():
    data = request.form 
    file = request.files['img']
    if file and not file.filename == '':
        register_patient(data,file.read(),'Out-Patient')
    else:
        register_patient(data,b'','Out-Patient')
    patient_login_update(data)

    return render_template('patient/patient.html')

@app.route('/update-prescription',methods=['POST'])
@flask_login.login_required
def update_prescription():
    data = request.json
    try:
        prescription_update(data)
        return  data
    except exception as e:
        return str(e)



## admin routes
@app.route('/admin-dashboard')

def admin_dashboard():
    docs = all_docs()
    patients = all_patients()
    apts = all_appointments()
    inpatientcount = len(all_inpatients())
    return render_template('admin/admin_dashboard.html',docs = docs,doc_count = len(docs),inpatientcount=inpatientcount,patient_count = len(patients),patient=patients,apt_count = len(apts))

@app.route('/admin-doctor')
def admin_doctor():
    return render_template('admin/admin_doctor.html')

@app.route('/admin-view-doctor')
def admin_view_doctor():
    docs = all_docs()
    return render_template('admin/admin_view_doctor.html',docs=docs)

@app.route('/admin-add-inpatient',methods=['POST','GET'])
def admin_add_patient():
    if request.method == 'GET':
        docs = all_docs()
        return render_template('admin/admin_patient_registration.html',docs=docs)
    if request.method == 'POST':
        file = request.files['img']
        data = request.form
        doc = get_doc_with_id(data['doc'])

        if file and not file.filename == '':
            register_patient_details(data,'In-Patient')
            patient_id = get_patient_details(data['email'])[0]
            register_inpatient(data['name'],data['diagnosis'],data['prescription'],data['doc'],doc[1],doc[2],data['date'],file.read(), patient_id)
        else:
            register_patient_details(data,'In-Patient')
            patient_id = get_patient_details(data['email'])[0]
            register_inpatient(data['name'],data['diagnosis'],data['prescription'],data['doc'],doc[1],doc[2],data['date'],b'', patient_id)

        return redirect(url_for('admin_add_patient'))
        

@app.route('/delete-appointment',methods=['POST'])
def delte_appointment():
    try:
        data = request.json
        cur.execute('delete from appointments where id=(?)',(data['id'],))
        con.commit()
        return "done"
    except:
        return 'error'
@app.route('/delete-patient',methods=['POST'])
def delte_patient():
    try:
        data = request.json
        email = get_patient_withid(data['id'])[1]
        cur.execute('delete from patient where id=(?)',(data['id'],))
        cur.execute('delete from patientlogin where email=(?)',(email,))
        con.commit()
        return "done"
    except  :
      
        return 'error'

@app.route('/admin-patient')
def admin_patient():
    patient = all_patients()
    return render_template('admin/admin_patient.html')
@app.route('/admin-view-patient')
def admin_view_patient():
    patient = all_patients()
    return render_template('admin/admin_view_patient.html',patient=patient)

@app.route('/admin-appointment')
def admin_appointment():
    apts = all_appointments()
    return render_template('admin/admin_view_appointment.html',apts=apts)

@app.route('/admin-add-doctor',methods=['GET','POST'])
def add_doctor():
    if request.method == 'GET':
        return render_template('admin/admin_add_doctor.html')
    elif request.method == 'POST':
        data = request.form
        admin_add_doctor_login(data)
        file = request.files['img']
        if file and not file.filename == '':   
            admin_add_doctor_details(data,file.read())
        else:
            admin_add_doctor_details(data,b'')
        return redirect(url_for('add_doctor'))

app.run(debug=True)