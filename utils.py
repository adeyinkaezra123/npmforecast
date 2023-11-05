def convert_to_days(option):
    PREDICTION_OPTIONS = {
        '1 Week': 7,
        '1 Month': 30,
        '3 Months': 90,
        '6 Months': 180,
        '1 Year': 365,
    }

    if option in PREDICTION_OPTIONS:
        return PREDICTION_OPTIONS[option]
    return PREDICTION_OPTIONS['1 Week']
