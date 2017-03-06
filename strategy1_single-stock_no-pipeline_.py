from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
def initialize(context):
    context.assets = sid(8554) # Trade SPY
    context.model = LogisticRegression()

    context.lookback = 1 # Look back 
    context.history_range = 400 

    # Generate a new model every week
    schedule_function(create_model, date_rules.week_end(), time_rules.market_close(minutes=10))

    # Trade at the start of every day
   
    schedule_function(trade, date_rules.every_day(), time_rules.market_open(minutes=1))

def create_model(context, data):
    # Get the relevant daily prices
    recent_prices = data.history(context.assets, 'price',context.history_range, '1d')
   
 
    time_lags = pd.DataFrame(index=recent_prices.index)
    time_lags['price']=recent_prices.values
    time_lags['returns']=(time_lags['price'].pct_change()).fillna(0.0001)
    time_lags['lag1'] = (time_lags['returns'].shift(1)).fillna(0.0001)
    time_lags['lag2'] = (time_lags['returns'].shift(2)).fillna(0.0001)
    time_lags['direction'] = np.sign(time_lags['returns'])
    
    
    X = time_lags[['lag1','lag2']] # Independent, or input variables
    Y = time_lags['direction'] # Dependent, or output variable
    context.model.fit(X, Y) # Generate our model

def trade(context, data):
    if context.model: # Check if our model is generated
        
        # Get recent prices
        new_recent_prices = data.history(context.assets,'price', context.lookback, '1d')
        
        time_lags = pd.DataFrame(index=new_recent_prices.index)
        time_lags['price']=new_recent_prices.values
        time_lags['returns']=(time_lags['price'].pct_change()).fillna(0.0001)
        time_lags['lag1'] = (time_lags['returns'].shift(1)).fillna(0.0001)
        time_lags['lag2'] = (time_lags['returns'].shift(2)).fillna(0.0001)
        
        X = time_lags[['lag1','lag2']]
        prediction = context.model.predict(X)
        if prediction > 0:
            order_target_percent(context.assets, 1.0)
        else:
            order_target_percent(context.assets, -1.0)

def handle_data(context, data):
    pass
