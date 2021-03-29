import json
import math


# pull me out to a strategy
def _linear_regression_analysis(data):
    # see https://realpython.com/linear-regression-in-python/
    import numpy as np
    from scipy import stats
    from sklearn.linear_model import LinearRegression
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
    return {
        "Coefficients": params.tolist(),
        "Standard Errors": sd_b.tolist(),
        "t values": ts_b.tolist(),
        "Probabilities": p_values.tolist()
    }


# def _polynomial_regression_analysis(data):
#     x = np.array(data[0])
#     y = np.array(data[1])
#     z = np.polyfit(x, y, 3)
#     p = np.poly1d(z)
#     xp = np.linspace(x.min(), x.max(), 100)
#
#     import matplotlib.pyplot as plt
#     plt.plot(x, y, '.', xp, p(xp), '-')
#     plt.show()


def _pretty_print_linear_regression_data(data):
    # class NDArrayEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         if isinstance(obj, np.ndarray):
    #             return obj.tolist()
    #         return json.JSONEncoder.default(self, obj)
    #
    # print(json.dumps(data, indent=2, sort_keys=True, cls=NDArrayEncoder))
    print(json.dumps(data, indent=2, sort_keys=True))


def analyze(data, verbose=True):
    if not data or len(data) < 2:
        return 'undetermined'
    print(data)
    # satisfactory: obi_force-AAR_java_statistics.json
    # satisfactory: obi_force-bowser-supplierfeed-service_java_statistics.json
    # problematic: obi_force-FENIX-FIRE-GlobalSoftwareUpdateGateway_java_statistics.json
    result = _linear_regression_analysis(data)
    if verbose:
        _pretty_print_linear_regression_data(result)
    first_t_value = result['t values'][0]
    # todo the trouble is here, probably need to look at more than just first_t_value
    if math.isnan(first_t_value):
        return 'satisfactory'  # is this right? I don't think it is
    if -1.96 < first_t_value < 1.96:
        return 'satisfactory'
    else:
        return 'problematic'
