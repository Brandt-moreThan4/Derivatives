"""Things to do:
- Have some function like "Plot Strategies"" which will just plot various strategies of an underlying. Ex: (calendar
  spread, bull spread, straddle, straggle, and anything else.
- Add puts
- Maybe add the ability to have a positions class. Which will be made up of a certain quantity of the security you are trading.
"""

import pandas as pd
import numpy as np
import seaborn as sns
from numpy.random import default_rng
from matplotlib import pyplot as plt
import datetime
from scipy.stats import norm
from utils import bsm

sns.set_theme()


class Underlying:
    """Class to represent some underlying. This will contain all of the information about a particular security which
    will be referenced by the derivatives based off of it."""

    def __init__(self, name: str, ticker: str = '', price: float = None, vol: float = .15):
        self.name = name
        self.ticker = ticker
        self.price = price
        self.vol = vol

    def __repr__(self):
        return self.ticker

    def __str__(self):
        return self.ticker


class Call:
    """Used to represent a european call option."""

    def __init__(self, underlying: Underlying, strike: float, expiration: datetime.date, risk_free_rate, cost: float = None,
                 pos_type='long'):

        self.underlying = underlying
        self.strike = strike
        self.expiration = expiration
        self.position_type = pos_type
        if cost is None:
            # If you do not provide a cost when creating this option then it will be assumed to be the BSM value.
            self.cost = self.calc_value(risk_free_rate)
        else:
            self.cost = cost

    def calc_payoff(self, underlying_price):
        """Send in an underlying price and this will return the value of exercising immediately."""
        payoff = max(underlying_price - self.strike, 0)
        if self.position_type != 'long':
            # The short payoff is simply the negative of the longs... right?
            payoff = -1 * payoff
        return payoff

    def calc_profit(self, underlying_price):
        """Profit for the option is simply the payoff at expiration minus the initial cost."""
        profit = self.calc_payoff(underlying_price) - self.cost
        return profit

    def calc_value(self, risk_free_rate: float, model=bsm):
        """Calculated the value using bsm as default. At some point, this should be extended so that you can input
        whichever pricing model you would like."""

        time_to_expire = (self.expiration - datetime.date.today()).days / 365
        # every model should expect the same arguments
        return model(self.underlying.price, self.strike, risk_free_rate, time_to_expire, self.underlying.vol)

    def get_top_price(self, percent_range: float = 2.0):
        """This will return an appropriate maximum price to use for payoff diagrams which will be based on
         a reasonable upper bound to depict on the diagram. The default upper bound is 200% above the strike.
         This may be necessary if some securities have dramatically different prices.
         """
        top_price = self.strike * percent_range
        return top_price

    def generate_payoff_range(self, price_array):
        """Send in an array or list of prices and this function will return an numpy array of the payoffs generated
        based on those prices."""

        payoffs = []
        for price in price_array:
            payoff = self.calc_payoff(price)
            payoffs.append(payoff)
        return np.array(payoffs)

    def generate_profit_range(self, price_array):
        """Send in an array or list of prices and this function will return an numpy array of the payoffs generated
        based on those prices."""

        payoffs = self.generate_payoff_range(price_array)
        profits = payoffs - self.cost
        return np.array(profits)

    def __repr__(self):
        return f'{self.position_type.title()} Call ({self.strike})'

    def __str__(self):
        return f'{self.position_type.title()} Call ({self.strike})'


class Portfolio:
    """The portfolio class will primarily be used to aggregate different positions to understand how they interact as
    a whole."""

    def __init__(self, positions: list):
        self.positions = positions

    def get_max_top_price(self):
        """This needs a better name, but it will return the maximum top price to be used based on all securities in the
        portfolio."""
        max_top_price = 0
        for position in self.positions:
            top_price = position.get_top_price()
            max_top_price = max(top_price, max_top_price)
        return max_top_price

    def plot_payoffs(self, bottom_price=0):
        """This function will plot the payoff diagram of each position separately, but all on the same graph."""

        # Price array from bottom price specified to the top price, incremented by a penny.
        prices = np.arange(bottom_price, self.get_max_top_price(), .01)

        fig, ax = plt.subplots()
        for position in self.positions:
            payoffs = position.generate_payoff_range(prices)
            ax.plot(prices, payoffs, label=str(position))

        ax.set_title('Security Payoffs by Underlying Price')
        ax.set_xlabel('Price')
        ax.set_ylabel('Payoff')
        ax.legend()

    def plot_payoffs_aggregate(self, bottom_price=0):
        """Plot the payoff diagram based on the portfolio as a whole."""
        prices = np.arange(bottom_price, self.get_max_top_price(), .01)
        combined_payoffs = np.zeros(len(prices))  # Start with payoff of 0 and add each position.
        for position in self.positions:
            position_payoffs = position.generate_payoff_range(prices)
            combined_payoffs = combined_payoffs + position_payoffs

        fig, ax = plt.subplots()
        ax.plot(prices, combined_payoffs)
        ax.set_title('Aggregate Portfolio Payoff by Underlying Price')
        ax.set_xlabel('Price')
        ax.set_ylabel('Payout')

    def get_profit_text(self):
        """Well this will ideally add a nice text description to the figure, but it's not that great."""
        position_text = ''
        for position in self.positions:
            position_text += f'{str(position)}\n'
        text = f"""
Portfolio containing:
{position_text}"""
        return text

    def plot_profits_agg(self, bottom_price=0):
        """This will be used to plot the profit of the portfolio as a whole."""
        prices = np.arange(bottom_price, self.get_max_top_price(), .01)
        combined_profits = np.zeros(len(prices))  # Start with payoff of 0 and add each position.
        for position in self.positions:
            position_profits = position.generate_profit_range(prices)
            combined_profits = combined_profits + position_profits

        fig, ax = plt.subplots()
        ax.plot(prices, combined_profits)
        ax.set_title('Aggregate Portfolio Profit by Underlying Price')
        ax.set_xlabel('Price')
        ax.set_ylabel('Profit')
        ax.text(0.25, 0.75, self.get_profit_text(), horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
