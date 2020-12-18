import csv
import pymongo
import time
from datetime import datetime
import matplotlib.pyplot as plt
import flask
from flask import request, jsonify


class BetsDatabase():
    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = self.myclient["mydatabase"]
        self.mycol = self.mydb['bets']
        self.tipsters = []
        self.no_of_bets = 0

    def create_db(self):
        print('Deleting old collection from mongoDB...')
        self.mycol.delete_many({})
        print('Creating new collection in mongoDB...')
        with open('/mnt/c/Users/spyro/Downloads/bettings-export-spyros2-20201217.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            dates_dict = {}
            for row in csv_reader:
                if line_count == 0:
                    pass
                else:
                    if row[7] != 'VOID':
                        x = self.mycol.insert_one({
                            '_id': line_count,
                            'date': row[0],
                            'game': row[2],
                            'selection': row[3],
                            'units': float(row[4]),
                            'odds': float(row[5]),
                            'result': row[6],
                            'profit': row[7],
                            'tipster': row[8]
                        })
                line_count +=1
        self.no_of_bets = line_count
        print('Collection created in mongoDB...')

    def get_result(self, tipster = None, date = None):
        units, profit = 0, 0
        myquery = {}
        if tipster:
            myquery['tipster'] = {"$regex": tipster}
        if date:
            myquery['date'] = {"$regex": date}
        mydoc = self.mycol.find(myquery)
        return mydoc

    def display_all(self):
        bets_json = []
        for x in self.mycol.find():
            bets_json.append(x)
        return bets_json

    @staticmethod
    def sum_profits(doc):
        my_sum = 0
        for x in doc:
            if x['result'] == 'WON' or x['result'] == 'LOST':
                my_sum += float(x['profit'])
        return my_sum

def get_bookie_results():
    with open('/mnt/c/Users/spyro/Downloads/bettings-export-spyros2-20201216.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        bookies_dict = {}
        for row in csv_reader:
            if line_count == 0:
                pass
            else:
                if row[7] != 'VOID':
                    if row[8] in bookies_dict:
                        bookies_dict[row[8]] += float(row[7])
                    else:
                        bookies_dict[row[8]] = float(row[7])
            line_count +=1
        print(bookies_dict)
      
def get_profit_per_day():
    with open('/mnt/c/Users/spyro/Downloads/bettings-export-spyros2-20201216.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        dates_dict = {}
        for row in csv_reader:
            if line_count == 0:
                pass
            else:
                if row[7] != 'VOID':
                    if row[0] in dates_dict:
                        dates_dict[row[0]] += float(row[7])
                    else:
                        dates_dict[row[0]] = float(row[7])
            line_count +=1
        print(dates_dict)
 
def get_result_month(month):
    days=list(range(1,31))
    results = []
    for day in days:
        results.append(sum_profits(get_result(date='2020-12-'+str(day).zfill(2))))
    print(results)
    plt.plot(days, results)
    plt.savefig('/mnt/c/Users/spyro/Desktop/test.png')

db = BetsDatabase()
db.create_db()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>Bullshit</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/display_all', methods=['GET'])
def display_all():
    return jsonify(db.display_all())

app.run()