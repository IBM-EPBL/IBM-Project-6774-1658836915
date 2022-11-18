from flask import Flask,render_template,redirect,url_for,request,session,flash,Blueprint
from re import fullmatch
from uuid import uuid4
from datetime import date
from customer import customer
import ibm_db
import json as JSON

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jym40126;PWD=1FiBds6gspiPRarV","","")

admin = Blueprint('admin',__name__)

@admin.route('/admin',methods=['GET','POST'])
def admin_login():
	if request.method == 'GET':
		return render_template('admin_login.html')
	elif request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		if email == 'abidarsh75@gmail.com' and password == '12345':
			session['admin'] = {'email':'a@gmail.com'}
			return render_template('admin_dashboard.html')
		else:
			flash('wrong credentials!!!')
			return redirect(url_for(admin.admin_login))

@admin.route('/admin/tickets')
def admin_tickets():
	sql = 'SELECT * FROM tickets'
	stmt = ibm_db.prepare(conn,sql)
	ibm_db.execute(stmt)
	ticket = ibm_db.fetch_assoc(stmt)
	unasign_tickets = []
	
	while ticket:
		if ticket['AGENT'] == 'None':
			unasign_tickets.append(ticket)

		ticket = ibm_db.fetch_assoc(stmt)
	
	sql = 'SELECT * FROM agents'
	stmt = ibm_db.prepare(conn,sql)
	ibm_db.execute(stmt)
	agent = ibm_db.fetch_assoc(stmt)
	approved = []

	while agent:
		if agent['APPROVED'] != 'None':
			approved.append(agent)
		agent = ibm_db.fetch_assoc(stmt)
	
	return render_template('admin_tickets.html',tickets=unasign_tickets,agents=approved)

@admin.route('/admin/requests')
def admin_requests():
	sql = 'SELECT * FROM agents'
	stmt = ibm_db.prepare(conn,sql)
	ibm_db.execute(stmt)
	agent = ibm_db.fetch_assoc(stmt)
	unapproved = []

	while agent:
		if agent['APPROVED'] == 'None':
			unapproved.append(agent)
		agent = ibm_db.fetch_assoc(stmt)

	print(unapproved)
	return render_template('admin_requests.html',agents = unapproved)

@admin.route('/admin/approve/<approval>/<agent>')
def admin_approve(approval,agent):
	sql = 'UPDATE agents SET APPROVED=? WHERE ID=?'
	stmt = ibm_db.prepare(conn,sql)
	ibm_db.bind_param(stmt,1,approval)
	ibm_db.bind_param(stmt,2,agent)
	ibm_db.execute(stmt)
	return 'ok'

@admin.route('/admin/agents')
def admin_agents():
	sql = 'SELECT * FROM agents'
	stmt = ibm_db.prepare(conn,sql)
	ibm_db.execute(stmt)
	agent = ibm_db.fetch_assoc(stmt)
	agents = []

	while agent:
		if agent['APPROVED'] == 'yes':
			agents.append(agent)
		agent = ibm_db.fetch_assoc(stmt)

	print(agents)
	return render_template('admin_agents.html',agents=agents)

@admin.route('/admin/logout')
def admin_logout():
	session.pop('admin')
	return redirect(url_for('customer.customer_login'))

@admin.route('/admin/assign/<ticket>/<agent>')
def admin_assign(ticket,agent):

	print(ticket,agent)
	sql = 'UPDATE tickets SET AGENT=? WHERE ID=?'
	stmt = ibm_db.prepare(conn,sql)
	ibm_db.bind_param(stmt,1,agent)
	ibm_db.bind_param(stmt,2,ticket)
	ibm_db.execute(stmt)
	return "ok"
