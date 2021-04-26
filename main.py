"""Until there is a GUI, this is how you can interact with the program"""

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from datetime import date, timedelta
from options import Call, Portfolio, Underlying

sns.set_theme()

RISK_FREE_RATE = .04  # Continuously compounded, annual risk free rate.


def main():
    luv_stock = Underlying(name='Southwest Airlines', ticker='LUV', price=100, vol=.2)

    # Create two options that expire in 51 days. One long, the other short.
    option_expiration = date.today() + timedelta(days=50)
    call = Call(underlying=luv_stock, strike=100, expiration=option_expiration, risk_free_rate=RISK_FREE_RATE)
    call2 = Call(underlying=luv_stock, strike=120, expiration=option_expiration, risk_free_rate=RISK_FREE_RATE, pos_type='short')

    positions = [call, call2]
    portfolio = Portfolio(positions=positions)

    # portfolio.plot_payoffs()
    # portfolio.plot_payoffs_aggregate()
    portfolio.plot_profits_agg()

    plt.show()


if __name__ == '__main__':
    main()
