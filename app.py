from flask import Flask, redirect, url_for, request, render_template, send_file
from spellchecker import SpellChecker
from werkzeug import secure_filename
import os

spell = SpellChecker()
app = Flask(__name__)

@app.route('/')
def hello_world():
    print ('test')
    return render_template('formpage.html')

@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name

@app.route('/return-file/')
def return_file():
    # os.remove("output.txt")

    return send_file('output.txt', attachment_filename='output.txt', cache_timeout=-1)

@app.route('/processing',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        message = request.form['message']
        misspelled = spell.unknown(str(message).split(' '))
        result = ' '
        for word in misspelled:
            # Get the one `most likely` answer
            result = result + spell.correction(word)
            result = result + " "
        return render_template('result.html',message=result)
    else:
        message = request.args.get('message')
        misspelled = spell.unknown(str(message).split(' '))
        result = ' '
        for word in misspelled:
            # Get the one `most likely` answer
            result = result + spell.correction(word)
            result = result + " "
        return render_template('result.html',message=result)

def check_file(f):
    fi = open(f.filename, "r")
    final = open("output.txt","w")
    misspelled = spell.unknown(str(fi.read()).split(' '))
    result = ' '
    for word in misspelled:
        # Get the one `most likely` answer
        result = result + spell.correction(word)
        result = result + " "
        print(result)
    final.write(result)
    final.close()
    fi.close()
    os.remove(f.filename)

@app.route('/uploader',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        #print(f.filename)
        check_file(f)
        return render_template('result.html',message="File uploaded Successsfuly")

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)