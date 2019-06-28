from flask import Flask, request, render_template
import pickle
import os.path
import sys
import asyncio

app = Flask(__name__, static_folder='static/', static_url_path='')

id_list = [{'item1': 'https://datastudio.google.com/embed/reporting/1BPUO86dh2Kdu5jNIdVepIh-73ACGDkr7/page/jr4s',
            'item2': 'https://datastudio.google.com/embed/reporting/18UA4eqZiruDn02J0mR2cLICn9bZImgQK/page/144s'}]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/backtesting.html')
def backtest():
    if request.args.get('id') is None:
        return render_template('backtesting.html')
    id = int(request.args.get('id')) - 1
    return render_template('backtesting.html', item1=id_list[id]['item1'], item2=id_list[id]['item2'])

@app.route('/modelUpload')
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save('models/' + f.filename)
        # produce history
        cc = ['005930', '000660', '005380', '068270', '051910', '012330', '055550', '005490', '051900', '017670']
        history = {}
        for c in cc:
            os.system('python evaluate.py {} {}'.format(c, f.filename))
            f = open('temp/res_{}.csv'.format(c), 'r')
            lines = f.readlines()
            for line in lines:
                dt, ct, pd, cp = line.split(',')
                if history[dt] is None:
                    history[dt] = {}
                history[dt][c] = {}
            f.close()
        return 'suc'
    return 'fail'

@app.route('/history')
def history():
    id = request.args.get('id')
    f = open('history/{}.csv', )

def model():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file'])
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = {'properties': {
        'title': 'Noooo'
    }}
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                    fields='spreadsheetId').execute()
    print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))
