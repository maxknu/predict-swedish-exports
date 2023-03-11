import pandas as pd
import numpy as np
from dbnomics import fetch_series, fetch_series_by_api_link

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

import os
import boto3
from dotenv import load_dotenv
load_dotenv()

# Monthly CPI
cpi = fetch_series("OECD", "KEI", series_code="CPALTT01.SWE.GP.M")
cpi = cpi.query("period >= '2015'")
cpi = cpi[['period','value']]
cpi= cpi.rename(columns = {'value':'cpi'})


# Monthly price index, Energy
ep = fetch_series("IMF", "PCPS", series_code="M.W00.PNRG.IX")
ep = ep.query("period >= '2015'")
ep = ep[['period','value']]
ep = ep.rename(columns = {'value':'energy_prices'})

ep.head()

# Monthly price index, Metals
mp = fetch_series("IMF", "PCPS", series_code="M.W00.PALLMETA.IX")
mp = mp.query("period >= '2015'")
mp = mp[['period','value']]
mp = mp.rename(columns = {'value':'metal_prices'})

# Monthly price index, Agriculture
ap = fetch_series("IMF", "PCPS", series_code="M.W00.PRAWM.IX")
ap = ap.query("period >= '2015'")
ap = ap[['period','value']]
ap = ap.rename(columns = {'value':'agri_prices'})

# Quarterly GDP 
gdp = fetch_series("OECD", "MEI", series_code="SWE.NAEXCP01.STSA.Q")
gdp = gdp.query("period >= '2015'")
gdp = gdp[['period','value']]
gdp = gdp.rename(columns = {'value':'gdp'})

# Quarterly Exports 
exports = fetch_series("OECD", "MEI", series_code="SWE.NAEXCP06.STSA.Q")
exports = exports.query("period >= '2015'")
exports = exports[['period','value']]
exports = exports.rename(columns = {'value':'exports'})

# Monthly confidence  
confidence = fetch_series("OECD", "KEI", series_code="BSCICP02.SWE.ST.M")
confidence = confidence.query("period >= '2015'")
confidence = confidence[['period','value']]
confidence = confidence.rename(columns = {'value':'confidence'})

# Exchange rates
excr = fetch_series("OECD", "KEI", series_code="CCUSMA02.SWE.ST.M")
excr = excr.query("period >= '2015'")
excr = excr[['period','value']]
excr = excr.rename(columns = {'value':'exch_rate'})

m = pd.merge(cpi, ep, on = 'period')
m = pd.merge(m, mp, on = 'period')
m = pd.merge(m, ap, on = 'period')
m = pd.merge(m, confidence, on = 'period')

m.head()

q = pd.merge(gdp, exports, on = 'period',  how = 'left')

# Move period defining quarter from the first to the last month 
q['period'] = q['period'] + pd.DateOffset(months=2)

q.head()

df = pd.merge(m,q, on = 'period', how = 'left')

df.head()

df['gdpm'] = df['gdp']/3
df['gdpm'] = df['gdpm'].fillna(method = 'bfill')

df['expm'] = df['exports']/3
df['expm'] = df['expm'].fillna(method = 'bfill')

df.tail(10)

df.drop(columns = ['gdp', 'exports'],  inplace = True)

df.rename(columns = {'gdpm': 'gdp', 'expm':'exports', 'period':'date'},  inplace = True)

df.head()

data = df

# Train and test split

# Dates
train_start_date = "2015-01-01"
train_end_date = "2020-03-01"
test_start_date = "2020-04-01"
test_end_date = "2020-12-01"

# Split
train = data.loc[(data['date']>= train_start_date) & (data['date'] <= train_end_date), :].reset_index(drop = True)
test = data.loc[(data['date'] >= train_start_date) & (data['date'] <= test_end_date), :].reset_index(drop = True)

# Target variable
target_variable = 'exports' 

# Impute by forward filling
train_processed = train.fillna(method = 'ffill')

# Impute remaining missing observations by backward filling
train_processed = train_processed.fillna(method = 'bfill')
train_processed.head()

# train 10 models to average outputs
models = []
for i in range(10):
    model = GradientBoostingRegressor(n_estimators = 100, 
                                      loss = "absolute_error", 
                                      max_depth = None, 
                                      min_samples_split = 2, 
                                      min_samples_leaf = 1)

    
    x = train_processed.drop(["date", target_variable], axis=1)
    y = train_processed[target_variable]
    
    model.fit(x, y)
    models.append(model)

# Pre-process test data
test_processed = test.fillna(method = 'ffill')
test_processed = test_processed.fillna(method = 'bfill')
test_processed.head()

y_true = test_processed[target_variable].values
y_true

y_pred = model.predict(test_processed.drop(["date", target_variable], axis=1))
y_pred

np.sqrt(mean_absolute_error(y_true, y_pred))

all_dates = test_processed['date']
all_dates

# plot of predictions vs test_values
pd.DataFrame({
    "true values":y_true, 
    "predictions":y_pred},
    index = all_dates).plot()

prediction_date = data['date'].max() 

data_pred = data.drop(['date', target_variable], axis = 1)

# Pre-process test data
data_pred_processed = data_pred.fillna(method = 'ffill')
data_pred_processed = data_pred_processed.fillna(method = 'bfill')

data_pred_processed.info()

preds = []
for i in range(10):
    prediction = models[i].predict(data_pred_processed)[0]
    preds.append(prediction)
        
y = np.nanmean(preds)
d = {'Date': prediction_date, 'Exports':[y]}

result = pd.DataFrame(d)
result

result.to_csv('predict_exports.csv', index=False)


##################################################################
##################################################################
# PART 2 #########################################################

aws_access_key_id = os.environ.get('aws_access_key_id')
aws_secret_access_key = os.environ.get('aws_secret_access_key')

# Set up S3 credentials
s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key)

# Set the name of the bucket and the path to your local file
bucket_name = os.environ.get('bucket_name')
file_path = 'predict_exports.csv'

# Upload the file to S3
s3.upload_file(file_path, bucket_name, 'prediction.csv')

print(f"{file_path} has been uploaded to {bucket_name} as prediction.csv.")
