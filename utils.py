import numpy as np
from scipy.stats import norm

def bsm(s, k, r, t, v, put=False):
    """Calculate the black-scholes-merton value of a european option. 'r' should be the continuously compounded
     risk free rate."""

    d1 = (np.log(s / k) + (r + (v ** 2) / 2) * t) / (v * np.sqrt(t))
    d2 = d1 - v * np.sqrt(t)
    if not put:
        option_value = norm.cdf(d1) * s - norm.cdf(d2) * k * np.exp(-r * t)
    else:
        # I have not tested this yet to make sure it works. It should tho.
        option_value = k * np.exp(-r * t) * norm.cdf(-d2) - s * norm.cdf(-d1)
    return option_value
