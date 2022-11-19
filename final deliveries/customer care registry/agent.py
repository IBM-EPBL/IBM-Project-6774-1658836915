from flask import Flask,render_template,redirect,url_for,request,session,flash,Blueprint
from re import fullmatch
from uuid import uuid4
from datetime import date
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jym40126;PWD=1FiBds6gspiPRarV","","")

agent = Blueprint('agent',__name__)

@agent.route('/signin/',methods=['GET','POST'])
def agent_signin():
    if request.method == 'GET':
        return render_template('agent_signin.html')

    elif request.method == 'POST':
        _id = str(uuid4())
        name = request.form['name']
        email = request.form['email']
        role = 'agent'
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
        
            sql = "SELECT * FROM agents WHERE EMAIL=?"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            if account:
                flash('Email already exists,login please')
                return redirect(url_for('agent.agent_login'))
            else:
                sql = 'INSERT INTO agents VALUES(?,?,?,?,?,?)'
                stmt = ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,name) 
                ibm_db.bind_param(stmt,2,email)
                ibm_db.bind_param(stmt,3,role)
                ibm_db.bind_param(stmt,4,password)
                ibm_db.bind_param(stmt,5,_id)
                ibm_db.bind_param(stmt,6,'None')
                ibm_db.execute(stmt)
                flash('Account created successfully!!!!')
                return redirect(url_for('agent.agent_login'))
        else:
            return redirect(url_for('agent.agent_signin'))

@agent.route('/login/',methods=['GET','POST'])
def agent_login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'agent'

        sql = 'SELECT * FROM agents WHERE EMAIL=? AND PASSWORD=? AND ROLE=?'
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.bind_param(stmt,3,role)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        session['agent'] = account
        print(session['agent'])
        if account:
            if account['APPROVED'] == 'yes':
                print('here1')
                return render_template('agent_dashboard.html')
            elif account['APPROVED'] == 'None':
                print('here2')
                return "Your request is under process"
            elif account['APPROVED'] == 'no':
                print('here3')
                return "Sorry your request has been rejected"
        else:
            flash('Wrong account credentials')
            return redirect(url_for('agent.agent_login'))

@agent.route('/profile/',methods=['GET','POST'])
def agent_profile():
    if request.method == 'GET':
        if session['agent']:
            cur_user = session['agent']
            print(cur_user)
            return render_template('agent_profile.html',user=cur_user)
        else:
            return redirect(url_for('agent.agent_login'))

@agent.route('/tickets/')
def agent_tickets():
    ticket = []
    _id = session['agent']['ID']
    sql = 'SELECT * FROM tickets'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    temp = ibm_db.fetch_assoc(stmt)
    while temp:
        if temp['AGENT'] == _id:
            ticket.append(temp)
        temp = ibm_db.fetch_assoc(stmt)
    print(len(ticket))
    return render_template('agent_tickets.html',tickets=ticket)

@agent.route('/change_password/',methods=['GET','POST'])
def agent_change_password():

    if request.method == 'GET':
        return render_template('agent_password.html')
    
    elif request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        _id = session['agent']['ID']
        
        flag = True
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        special_chars = ('!','@','$','%','(',')','*','-','+','?','/','\\','.',',')

        if password == '' or confirm_password == '':
            flag = False
            flash('Passwords cannot be empty')

        if password != confirm_password:
            flag = False
            flash('Passwords donot match')

        if password == session['agent']['PASSWORD']:
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
            sql = 'UPDATE agents SET PASSWORD=? WHERE ID=?'
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,password)
            ibm_db.bind_param(stmt,2,_id)
            ibm_db.execute(stmt)
            flash('Password updated successfully')
            return redirect(url_for('agent.agent_logout'))
        else:
            return redirect(url_for('agent.change_password'))

@agent.route('/logout/')
def agent_logout():
    session.pop('agent')
    return redirect(url_for('agent.agent_login'))