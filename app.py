from flask import Flask, redirect, url_for, request, render_template
from spellchecker import SpellChecker

spell = SpellChecker()
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('formpage.html')

@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name

@app.route('/processing',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        message = request.form['message']
        misspelled = spell.unknown(str(message).split(' '))
        result = ' '
        for word in misspelled:
            # Get the one `most likely` answer
            result = result + spell.correction(word)
            result = result + "\n"
        return render_template('result.html',message=result)
    else:
        message = request.args.get('message')
        misspelled = spell.unknown(str(message).split(' '))
        result = ' '
        for word in misspelled:
            # Get the one `most likely` answer
            result = result + spell.correction(word)
            result = result + "\n"
        return render_template('result.html',message=result)

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)