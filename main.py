from flask import Flask, request, render_template
import pickle
import os.path
import sys
import json

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

@app.route('/model', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save('models/' + f.filename)
        # produce history
        cc = ['005930', '000660', '005380', '068270', '051910', '012330', '055550', '005490', '051900', '017670']
        history = {}
        for c in cc:
            os.system('python evaluate.py {} {}'.format(c, f.filename))
            csv = open('temp/res_{}.csv'.format(c), 'r')
            lines = csv.readlines()
            for line in lines:
                # date, count, cash, portfolio ,current price
                dt, ct, ch, pd, cp = line.strip().split(',')
                if not dt in history:
                    history[dt] = {}
                history[dt][c] = [ct, ch, pd, cp]
            csv.close()
        pi = open('result/{}.pickle'.format(f.filename), 'wb')
        pickle.dump(history, pi, protocol=pickle.HIGHEST_PROTOCOL)
        pi.close()
        return app.send_static_file('model_result.html')
    return 'fail'

@app.route('/history')
def history():
    mdl = request.args.get('model')
    pi = open('result/{}.pickle'.format(mdl), 'rb')
    history = pickle.load(pi)
    pi.close()
    pf = {}
    cc = ['005930', '000660', '005380', '068270', '051910', '012330', '055550', '005490', '051900', '017670']
    for c in cc:
        pf[c] = {}
    li = []
    for d in sorted(history.keys()): # date
        for c in history[d]: # code
            pf[c]['cnt'] = history[d][c][0]
            pf[c]['cash'] = history[d][c][1]
            pf[c]['pf'] = history[d][c][2]
        daily_pf = 0
        for c in pf:
            daily_pf += float(pf[c]['pf'])
        li.append(daily_pf)
    
    today = {}
    cash = 0
    for c in pf:
        cash += float(pf[c]['cash'])
        today[c] = float(pf[c]['pf']) - float(pf[c]['cash'])
    today['cash'] = cash
    return json.dumps(today)
    # f = open('history/{}.csv', )
