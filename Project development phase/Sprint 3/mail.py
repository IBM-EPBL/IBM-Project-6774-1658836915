# importing libraries
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app) # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rogman19fawkes@gmail.com'
app.config['MAIL_PASSWORD'] = 'ucfk snif djtd diuk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# message object mapped to a particular URL ‘/’
@app.route("/<receiver>")
def index(receiver):
	msg = Message(
				'Hello',
				sender ='noreply@gmail.com',
				recipients = [receiver]
			)
	msg.body = 'Hello Flask message sent from Flask-Mail'
	mail.send(msg)
	return 'Sent'

if __name__ == '__main__':
	app.run(debug = True)
