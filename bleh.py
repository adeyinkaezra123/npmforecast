from plotly.graph_objects import Figure
from datetime import datetime, timedelta

fig = Figure({
    'data': [{'mode': 'lines',
              'name': 'react',
              'type': 'scatter',
              'x': array([datetime.date(2023, 11, 5), datetime.date(2023, 11, 6),
                          datetime.date(2023, 11, 7), datetime.date(2023, 11, 8),
                          datetime.date(2023, 11, 9), datetime.date(2023, 11, 10),
                          datetime.date(2023, 11, 11)], dtype=object),
              'y': array([ 0, 2791866, 3006106, 2760208, 1317021,  300478,  364209])}],
    'layout': {'template': '...',
               'title': {'text': 'NPM Module Download Rate Prediction'},
               'xaxis': {'title': {'text': 'Timeframe'}},
               'yaxis': {'title': {'text': 'Estimated Downloads'}}}
})
fig.show()