import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression


def analyze(data):
    result = 'undetermined'
    x = np.array(data[0]).reshape((-1, 1))
    y = np.array(data[1])
    model = LinearRegression().fit(x, y)
    params = np.append(model.intercept_, model.coef_)
    predictions = model.predict(x)
    newX = np.append(np.ones((len(x), 1)), x, axis=1)
    MSE = (sum((y - predictions) ** 2)) / (len(newX) - len(newX[0]))
    var_b = MSE * (np.linalg.inv(np.dot(newX.T, newX)).diagonal())
    sd_b = np.sqrt(var_b)
    ts_b = params / sd_b
    p_values = [2 * (1 - stats.t.cdf(np.abs(i), (len(newX) - len(newX[0])))) for i in ts_b]
    sd_b = np.round(sd_b, 3)
    ts_b = np.round(ts_b, 3)
    p_values = np.round(p_values, 3)
    params = np.round(params, 4)
    result = {
        "Coefficients": params,
        "Standard Errors": sd_b,
        "t values": ts_b,
        "Probabilities": p_values
    }
    return result
