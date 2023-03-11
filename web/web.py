import boto3
import csv
import urllib.request
from flask import Flask, render_template

app = Flask(__name__)

s3 = boto3.client('s3')
bucket_name = 'storage-workato'
file_name = 'https://storage-workato.s3.eu-central-1.amazonaws.com/prediction.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjENf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMyJIMEYCIQDuTKuoBPLzStm1C7pnGb7QWaWgPTF%2BM8kzwOTODHE6NgIhAPCUZEkeqtLWtr8cLm7xMpXopqLemLQbL9Pti8JFHFDHKu0CCJD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQABoMMjkwMzk1NzgxMTA2IgyrBcpO2dFOs2EEdjkqwQLS66gvlozeeOvXCdrmHrL21mIXNMtWN4%2BX9tom2ihsW7mMztNxfvqcyT3pVNK3RwQyyz%2Fb%2FyAWZ1TKisZNb6NgP2YNn7TJsL%2Bbk95L5Z%2BSylyZViAtNxfkuWcurzmLiTfMd1DaaA2%2FBpuQNk2gq6JVDtm7WIvTsNiJZciHF7KwS5LFN0woLSry8jGqFU%2F37aFyJ2acxvTPDPxMHEUyZpNanBDm%2BkHs17p3Xqj2Bi81%2BduoWgx0ZA7W2A0hoJgbxNPL0txbcGPed363bRJGBPjNFpvGPosnNL8vV%2FEbVlwBloXBHj93IM0LoGD9a5n39v3SPbeTcmY9BxG9U4sUiigPbPnxtDCJyMUI7t4q2f9qrg3lAMst3CP2Ebw9Zx3zIG%2FXpnyCt10wZmd7IGBjE8ETCKzM7QQCySuswLrIv1g68Lcwm6uyoAY6sgK1YfvottWsQRAmAOH%2Fqm2Kt2qD6wXiyRACw0DoMl0og1plbHJEM3XezL%2BurUJ01wt9tr2kQemxbxnp5xL1%2BHl%2Bsq5oK0p8fCfEuo%2B880gsMRFTpg2AonOniI1o1IMKaQXrgIwqHQHgEjr62Abyqy3x9iHzt58uN6iC7uRYK7N3VwzlSN8ScYXGt0dhEN%2F8PC9Dci6P4rQj%2Fw0sBq4cbLl0K2hwGPf026MuEKgmbg9cN9Ghh3a%2FUpq1De3hGEA%2FcFeQTrr0O2NlIIrn0MW3%2BSBk2p9J9LFjg6co%2Ftw%2FMN8MLwy6GGM7T9P6c0MAcD8gzpfNnXdd6tnwPi%2FU%2F8qf96ggV2cTMJ4RvW9kG73pNHHeNynAFIzu%2FP5E6gqaLkmg0%2BHGtDHR3boLJHuCoTH8a4Db%2BqI%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230311T155146Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAUHHHP67ZG27XLF46%2F20230311%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=6e9f96547ebf2c6e4fa4ca5399800e58d4c4d2316b1fcc32233b0b1d7c64cd1d'

@app.route('/')
def index():
    data = []
    
    with urllib.request.urlopen(file_name) as url:
        reader = csv.DictReader(url.read().decode('utf-8').splitlines())
        for row in reader:
            data.append(row)
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
