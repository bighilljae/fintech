from flask import Flask, request, render_template, redirect
import math
import pickle
import os.path
import sys
import json

app = Flask(__name__, static_folder='static/', static_url_path='')

id_list = [{'item1': 'https://datastudio.google.com/embed/reporting/1BPUO86dh2Kdu5jNIdVepIh-73ACGDkr7/page/jr4s',
            'item2': 'https://datastudio.google.com/embed/reporting/18UA4eqZiruDn02J0mR2cLICn9bZImgQK/page/144s'}]
#     삼성전자,    현대차,    POSCO,    현대모비스,  LG화학,    한국전력,   SK하이닉스, 신한지주, NAVER, KB
cc = ['005930', '005380', '005490', '012330', '051910', '015760', '000660', '055550', '035420', '105560']

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
        l = open('result/list.txt', 'a+')
        l.write('{}\n'.format(f.filename))
        l.close()
        return redirect('/model_result.html?model={}'.format(f.filename))
        # return app.send_static_file('model_result.html')
    return 'fail'

@app.route('/history')
def history():
    mdl = request.args.get('model')
    pi = open('result/{}.pickle'.format(mdl), 'rb')
    history = pickle.load(pi)
    pi.close()
    pf = {}
    scale = {
        '000660': 100,
        '005380': 1000,
        '005490': 1000,
        '005930': 100,
        '012330': 1000,
        '015760': 100,
        '035420': 100,
        '051910': 1000,
        '055550': 100,
        '105560': 100
    }
    order_queue = {}
    
    for c in cc:
        pf[c] = {}
        order_queue[c] = {'cnt': 0, 'queue': []}
    li = []
    transaction = []
    dates = sorted(history.keys())
    for i,d in enumerate(dates):  # date
        for c in history[d]: # code
            pf[c]['cnt'] = history[d][c][0]
            pf[c]['cash'] = history[d][c][1]
            pf[c]['pf'] = history[d][c][2]

            if int(history[d][c][0]) > order_queue[c]['cnt']:
                transaction.append({
                    'date': d,
                    'code': c,
                    'cnt': int(history[d][c][0]) - order_queue[c]['cnt'],
                    'price': float(history[d][c][3]) * scale[c],
                    'profit': '-'})
                order_queue[c]['queue'].append(float(history[d][c][3]) * scale[c])
            if int(history[d][c][0]) < order_queue[c]['cnt']:
                transaction.append({
                    'date': d,
                    'code': c,
                    'cnt': int(history[d][c][0]) - order_queue[c]['cnt'],
                    'price': float(history[d][c][3]) * scale[c],
                    'profit': (float(history[d][c][3]) * scale[c] - order_queue[c]['queue'].pop(0)) * (order_queue[c]['cnt'] - int(history[d][c][0]))})
            order_queue[c]['cnt'] = int(history[d][c][0])
            
        daily_pf = 0
        for c in pf:
            daily_pf += float(pf[c]['pf'])
        li.append(daily_pf)

    
    today = []
    cash = 0
    for c in pf:
        cash += float(pf[c]['cash'])
        today.append(float(pf[c]['pf']) - float(pf[c]['cash']))
        # today[c] = float(pf[c]['pf']) - float(pf[c]['cash'])
    today.append(cash)
    #today['cash'] = cash
    
    return json.dumps({'li': li, 'xlabel': sorted(history.keys()), 'today': today, 'transaction': transaction})
    # f = open('history/{}.csv', )

@app.route('/model_list')
def model_list():
    f = open('result/list.txt', 'r')
    models = f.readlines()
    res = []

    for model in models:
        pi = open('result/{}.pickle'.format(model.strip()), 'rb')
        history = pickle.load(pi)
        pi.close()

        dates = sorted(history.keys())
        last_pf = 0
        for c in history[dates[-1]]:
            last_pf += float(history[dates[-1]][c][2])
        first_pf = 0
        for c in history[dates[0]]:
            first_pf += float(history[dates[0]][c][2])
        
        import datetime
        ee = datetime.datetime.strptime(dates[-1], '%Y-%m-%d')
        ss = datetime.datetime.strptime(dates[0], '%Y-%m-%d')
        yy = (ee - ss).days / 365
        rate = math.log(last_pf / first_pf) / yy * 10000
        res.append({'name': model, 'rate': round(rate) / 100})
    f.close()
    res.sort(key=lambda item: item['rate'], reverse=True)
    return render_template('user_model_list.html', model_list=res)
