from flask import Flask, request, render_template
app = Flask(__name__, static_folder='static/', static_url_path='')

id_list = [{'item1': 'https://datastudio.google.com/embed/reporting/1BPUO86dh2Kdu5jNIdVepIh-73ACGDkr7/page/jr4s',
            'item2': 'https://datastudio.google.com/embed/reporting/18UA4eqZiruDn02J0mR2cLICn9bZImgQK/page/144s'}]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/user_model_list.html')
def backtest():
    if request.args.get('id') is None:
        return render_template('user_model_list.html')
    id = int(request.args.get('id')) - 1
    return render_template('user_model_list.html', item1=id_list[id]['item1'], item2=id_list[id]['item2'])

@app.route('/modelUpload')
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save('model/' + f.filename)
        return 'suc'
    return 'fail'
