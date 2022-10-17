from flask import Flask,render_template,redirect,Request
app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
    if request.method =='GET':
        return render_template('assignment2.html')
    elif request.method =='POST':
        name = request.form['name']
        email = request.form['email']
        gender = request.form['gender']
        qualification = request.form['qualification']
        return render_template('table.html',details=list(name,email,gender,qualification))

if __name__ == '__main__':
    app.run(debug=True)
