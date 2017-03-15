#from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.qda import QDA
from sklearn import tree
#from sklearn.neural_network import MLPClassifier
import numpy as np
import pandas as pd

def initialize(context):
    context.assets = sid(8554) # Trade SPY
    context.model = LogisticRegression()
    context.lookback = 4 # Look back 
    context.history_range = 400 

    # Generate a new model every week
    schedule_function(create_model, date_rules.week_start(),time_rules.market_open(minutes=1))

    # Trade at the start of every day
   
    schedule_function(trade, date_rules.week_end(), time_rules.market_open(minutes=1))

def create_model(context, data):
    # Get the relevant daily prices
    recent_prices = data.history(context.assets, 'price',context.history_range, '1d')
   
    context.ma_50 =recent_prices.values[-50:].mean()     
    context.ma_200 = recent_prices.values[-200:].mean() 
    #print context.ma_50
    #print context.ma_200
    time_lags = pd.DataFrame(index=recent_prices.index)
    time_lags['price']=recent_prices.values
    time_lags['returns']=(time_lags['price'].pct_change()).fillna(0.0001)
    time_lags['lag1'] = (time_lags['returns'].shift(1)).fillna(0.0001)
    time_lags['lag2'] = (time_lags['returns'].shift(2)).fillna(0.0001)
    time_lags['direction'] = np.sign(time_lags['returns'])
    
    
    X = time_lags[['lag1','lag2']] # Independent, or input variables
    Y = time_lags['direction'] # Dependent, or output variable
   # print X
    #print X
    context.model.fit(X, Y) # Generate our model
    #print context.model.predict(X)
def trade(context, data):
    if context.model: # Check if our model is generated
        
        # Get recent prices
        new_recent_prices = data.history(context.assets,'price', context.lookback, '1d')
        
        time_lags = pd.DataFrame(index=new_recent_prices.index)
        time_lags['price']=new_recent_prices.values
        time_lags['returns']=(time_lags['price'].pct_change()).fillna(0.0001)
        time_lags['lag1'] = (time_lags['returns'].shift(1)).fillna(0.0001)
        
        X = time_lags[['returns','lag1']]
        prediction = context.model.predict(X)
        print prediction
        if prediction > 0 and context.ma_50 > context.ma_200:
            order_target_percent(context.assets, 1.0)
        elif prediction < 0 and context.ma_50 < context.ma_200:
            order_target_percent(context.assets, -1.0)
        else:
            pass
        
def handle_data(context, data):
    pass
