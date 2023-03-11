import boto3
import csv
import urllib.request
from flask import Flask, render_template

app = Flask(__name__)

s3 = boto3.client('s3')
bucket_name = 'storage-workato'
file_name = 'https://storage-workato.s3.eu-central-1.amazonaws.com/prediction.csv'

@app.route('/')
def index():
    data = []
    
    with urllib.request.urlopen(file_name) as url:
        reader = csv.DictReader(url.read().decode('utf-8').splitlines())
        for row in reader:
            print(row)
            data.append(row)
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
