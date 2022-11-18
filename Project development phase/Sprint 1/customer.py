from flask import Flask,render_template,redirect,url_for,request,session,flash,Blueprint
from re import fullmatch
from uuid import uuid4
from datetime import date
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jym40126;PWD=1FiBds6gspiPRarV","","")

customer = Blueprint('customer',__name__)

@customer.route('/signin',methods=['GET','POST'])
def customer_signin():
    if request.method == 'GET':
        return render_template('signin.html')

    elif request.method == 'POST':
        _id = str(uuid4())
        name = request.form['name']
        email = request.form['email']
        role = 'customer'
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        special_chars = ('!','@','$','%','(',')','*','-','+','?','/','\\','.',',')
        flag = True

        if name=='' or email=='' or password=='' or confirm_password=='' or role=='':
            flash('Fill empty details please!!!!')
            flag = False

        if not(fullmatch(regex,email)):
            flash('Enter valid email')
            flag = False
        
        if password != confirm_password:
            flash('Passwords doesn\'t match!!!')
            flag = False

        if not any(x.isupper() for x in password):
            flash('Use an uppercase in password')
            flag = False

        if not any(x.isdigit() for x in password):
            flash('Use a number in password')
            flag = False

        if not any(x in special_chars for x in password):
            flash('Use special characters in password!')
            flag = False
        
        if flag:
            sql = "SELECT * FROM customers WHERE EMAIL=?"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            if account:
                flash('Email already exists,login please')
                return redirect(url_for('customer.login'))
            else:
                sql = 'INSERT INTO customers VALUES(?,?,?,?,?)'
                stmt = ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,name) 
                ibm_db.bind_param(stmt,2,email)
                ibm_db.bind_param(stmt,3,role)
                ibm_db.bind_param(stmt,4,password)
                ibm_db.bind_param(stmt,5,_id)
                ibm_db.execute(stmt)
                flash('Account created successfully!!!!')
                return redirect(url_for('customer.customer_login'))
        else:
            return redirect(url_for('customer.customer_signin'))

@customer.route('/login',methods=['GET','POST'])
def customer_login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'customer'

        sql = 'SELECT * FROM customers WHERE EMAIL=? AND PASSWORD=? AND ROLE=?'
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.bind_param(stmt,3,role)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        session['user'] = account
        print(session['user'])
        if account:
            flash('logged in successfully')
            return render_template('customer_dashboard.html',name=session['user']['NAME'])
        else:
            flash('Wrong account credentials')
            return redirect(url_for('customer.customer_login'))

@customer.route('/profile',methods=['GET','POST'])
def profile():
    if request.method == 'GET':
        if session['user']:
            cur_user = session['user']
            print(cur_user)
            return render_template('customer_profile.html',user=cur_user)
        else:
            return redirect(url_for('customer.customer_login'))

@customer.route('/create_ticket',methods=['GET','POST'])
def create_ticket():
    
    if request.method == 'GET':
        return render_template('customer_create_ticket.html')
    
    elif request.method == 'POST':
        user = session['user']['ID']
        agent = 'None'
        query = request.form['query']
        date1 = str(date.today())
        _id = str(uuid4())
        status = 'Open'
        print(date1)

        if query == '':
            flash('Query cannot be empty')
            return redirect(url_for('customer.create_ticket'))
        else:    
            sql = 'INSERT INTO tickets VALUES(?,?,?,?,?,?)'
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,user)
            ibm_db.bind_param(stmt,2,agent)
            ibm_db.bind_param(stmt,3,query)
            ibm_db.bind_param(stmt,4,date1)
            ibm_db.bind_param(stmt,5,status)
            ibm_db.bind_param(stmt,6,_id)
            ibm_db.execute(stmt)
            flash('Ticket created successfully')
            return redirect(url_for('customer.create_ticket'))

@customer.route('/tickets')
def tickets():
    ticket = []
    _id = session['user']['ID']
    sql = 'SELECT * FROM tickets'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    temp = ibm_db.fetch_assoc(stmt)
    while temp:
        if temp['USER'] == _id:
            ticket.append(temp)
        temp = ibm_db.fetch_assoc(stmt)
    print(len(ticket))
    return render_template('customer_tickets.html',tickets=ticket)

@customer.route('/change_password',methods=['GET','POST'])
def change_password():

    if request.method == 'GET':
        return render_template('customer_password.html')
    
    elif request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        _id = session['user']['ID']
        
        flag = True
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        special_chars = ('!','@','$','%','(',')','*','-','+','?','/','\\','.',',')

        if password == '' or confirm_password == '':
            flag = False
            flash('Passwords cannot be empty')

        if password != confirm_password:
            flag = False
            flash('Passwords donot match')

        if password == session['user']['PASSWORD']:
            flag = False
            flash('Same as old password!!!')

        if not any(x.isupper() for x in password):
            flash('Use an uppercase in password')
            flag = False

        if not any(x.isdigit() for x in password):
            flash('Use a number in password')
            flag = False

        if not any(x in special_chars for x in password):
            flash('Use special characters in password!')
            flag = False
            
        if flag:
            sql = 'UPDATE customers SET PASSWORD=? WHERE ID=?'
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,password)
            ibm_db.bind_param(stmt,2,_id)
            ibm_db.execute(stmt)
            flash('Password updated successfully')
            return redirect(url_for('customer.customer_logout'))
        else:
            return redirect(url_for('customer.change_password'))

@customer.route('/logout')
def customer_logout():
    session.pop('user')
    return redirect(url_for('customer.customer_login'))