from sklearn.ensemble import RandomForestRegressor
from sklearn import preprocessing
import numpy as np

import pandas as pd
def initialize(context):
    context.assets = sid(8554) # Trade SPY
    context.model = RandomForestRegressor()

    context.lookback = 5 # Look back 
    context.history_range = 200 

    # Generate a new model every week
    schedule_function(create_model, date_rules.week_end(), time_rules.market_close(minutes=10))

    # Trade at the start of every day
   
    schedule_function(trade, date_rules.every_day(), time_rules.market_open(minutes=1))

def create_model(context, data):
    # Get the relevant daily prices
    recent_prices = data.history(context.assets, 'price',context.history_range, '1d')
   
    context.ma_50 =recent_prices.values[-50:].mean()     
    context.ma_200 = recent_prices.values[-200:].mean() 
    #print context.ma_50
    #print context.ma_200
    time_lags = pd.DataFrame(index=recent_prices.index)
    time_lags['price']=recent_prices.values
    time_lags['daily_returns']=time_lags['price'].pct_change()
    time_lags['multiple_day_returns'] =  time_lags['price'].pct_change(3)
    time_lags['rolling_mean'] = time_lags['daily_returns'].rolling(window = 4,center=False).mean()
    
    time_lags['time_lagged'] = time_lags['price']-time_lags['price'].shift(-2)
    X = time_lags[['price','daily_returns','multiple_day_returns','rolling_mean']].dropna()
        
    time_lags['updown'] = time_lags['daily_returns']
    time_lags.updown[time_lags['daily_returns']>=0]='up'
    time_lags.updown[time_lags['daily_returns']<0]='down'
    le = preprocessing.LabelEncoder()
    time_lags['encoding']=le.fit(time_lags['updown']).transform(time_lags['updown'])
  #  X = time_lags[['lag1','lag2']] # Independent, or input variables
   # Y = time_lags['direction'] # Dependent, or output variable
    context.model.fit(X,time_lags['encoding'][4:]) # Generate our model

def trade(context, data):
    if context.model: # Check if our model is generated
        
        # Get recent prices
        recent_prices = data.history(context.assets,'price',context.lookback, '1d')
        
        time_lags = pd.DataFrame(index=recent_prices.index)
        time_lags['price']=recent_prices.values
        time_lags['daily_returns']=time_lags['price'].pct_change()
        time_lags['multiple_day_returns'] =  time_lags['price'].pct_change(3)
        time_lags['rolling_mean'] = time_lags['daily_returns'].rolling(window = 4,center=False).mean()
    
        time_lags['time_lagged'] = time_lags['price']-time_lags['price'].shift(-2)
        X = time_lags[['price','daily_returns','multiple_day_returns','rolling_mean']].dropna()
   
        prediction = context.model.predict(X)
        if prediction == 1 and context.ma_50 > context.ma_200:
            order_target_percent(context.assets, 1.0)
        elif prediction == 2 and context.ma_50 < context.ma_200:
            order_target_percent(context.assets, -1.0)
        else:
            pass
        
def handle_data(context, data):
    pass
