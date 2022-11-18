from flask import Flask,render_template,redirect,url_for,request,session,flash,Blueprint
from re import fullmatch
from uuid import uuid4
from datetime import date
from flask_mail import Mail, Message
import ibm_db

#conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jym40126;PWD=1FiBds6gspiPRarV","","")


app = Flask(__name__)
mail = Mail(app) 

app.secret_key = 'hello'

from customer import customer
from agent import agent
from admin import admin

app.register_blueprint(customer)
app.register_blueprint(agent)
app.register_blueprint(admin)

@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')
   
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rogman19fawkes@gmail.com'
app.config['MAIL_PASSWORD'] = 'ucfk snif djtd diuk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

@app.route("/mail")
def send_mail(header,recipient,content):
   msg = Message(
                header,
                sender ='noreply@email.com',
                recipients = [recipient]
               )
   msg.body = content
   mail.send(msg)
   return 'Sent'

send_mail('title','annamalai19.sethu@gmail.com','hello')

@app.route('/tickets/query/mail',methods=['GET','POST'])
def query_mail():

    if request.method == 'GET':
        params = request.args.get('id')
        print(params)

        sql = 'SELECT * FROM tickets WHERE ID=?'
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,params)
        ibm_db.execute(stmt)
        tickets = ibm_db.fetch_assoc(stmt)

        print(tickets)

        return render_template('agent_mail.html',ticket=tickets)

    elif request.method == 'POST':
        status = 'close'
        _id = request.form['id']
        answer = request.form['reply']
        receiver = request.form['to']
        subject = request.form['qn']
        try:
            send_mail(subject, receiver, subject)
        except:
            return 'Mail not sent'
        else:
            sql = 'UPDATE tickets SET STATUS=? WHERE ID=?'
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,status)
            ibm_db.bind_param(stmt,2,_id)
            ibm_db.execute(stmt)
        
            ticket = []
            status = 'open'
            sql = 'SELECT * FROM tickets WHERE STATUS=?'
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,status)
            ibm_db.execute(stmt)
            temp = ibm_db.fetch_assoc(stmt)
            while temp:
                ticket.append(temp)
                temp = ibm_db.fetch_assoc(stmt)
            print(ticket)
        return redirect(url_for('agent.agent_tickets',tickets=ticket))
        

if __name__ == '__main__':
    app.run(debug=True)

