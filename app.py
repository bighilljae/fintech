from flask import Flask, request, render_template
app = Flask(__name__, static_folder='static/', static_url_path='')

id_list = [{'item1': 'https://datastudio.google.com/embed/reporting/1BPUO86dh2Kdu5jNIdVepIh-73ACGDkr7/page/jr4s',
            'item2': 'https://datastudio.google.com/embed/reporting/18UA4eqZiruDn02J0mR2cLICn9bZImgQK/page/144s'}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backtesting.html')
def backtest():
    print(request.args.get('id'))
    if request.args.get('id') is None:
        return render_template('backtesting.html')
    id = int(request.args.get('id')) - 1
    return render_template('backtesting.html', item1=id_list[id]['item1'], item2=id_list[id]['item2'])

if __name__ == '__main__':
    app.run(port=8080, debug=True)