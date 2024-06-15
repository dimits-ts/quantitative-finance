import enum
import abc
import random
from math import exp, sqrt


class OptionType(enum.Enum):
    """
    Enumeration for the type of options.

    :ivar CALL: Represents a call option.
    :ivar PUT: Represents a put option.
    """
    CALL = enum.auto()
    PUT = enum.auto()


class Option(abc.ABC):
    """
    Abstract base class for financial options.

    :param option_type: The type of the option (CALL or PUT).
    :type option_type: OptionType

    :param current_stock_price: The current price of the underlying stock.
    :type current_stock_price: float

    :param strike_price: The strike price of the option.
    :type strike_price: float

    :param interest: The risk-free interest rate from now until end-of-maturity.
    :type interest: float

    :param volatility: The volatility of the underlying stock.
    :type volatility: float

    :param dividend_yield: The dividend yield of the underlying stock.
    :type dividend_yield: float

    :param steps: The number of steps in the binomial tree model.
    :type steps: int
    """

    def __init__(self,
                 option_type: OptionType,
                 current_stock_price: float,
                 strike_price: float,
                 interest: float,
                 volatility: float,
                 dividend_yield: float,
                 steps: int):
        self.strike_price = strike_price
        self.steps = steps
        self.dividend_yield = dividend_yield
        self.volatility = volatility
        self.interest = interest
        self.current_stock_price = current_stock_price
        self.option_type = option_type

    @abc.abstractmethod
    def price(self) -> float:
        """
        Calculate the price of the option.

        :return: The price of the option.
        :rtype: float
        """
        return 0

    def _payoff(self, stock_price: float) -> float:
        """
        Calculate the payoff of the option at a given stock price.

        :param stock_price: The price of the underlying stock.
        :type stock_price: float

        :return: The payoff of the option.
        :rtype: float
        """
        if self.option_type == OptionType.CALL:
            return max(0., stock_price - self.strike_price)
        elif self.option_type == OptionType.PUT:
            return max(0., self.strike_price - stock_price)


class AmericanOption(Option):
    """
    Class for American options.

    :param option_type: The type of the option (CALL or PUT).
    :type option_type: OptionType

    :param current_stock_price: The current price of the underlying stock.
    :type current_stock_price: float

    :param strike_price: The strike price of the option.
    :type strike_price: float

    :param interest: The risk-free interest rate from now until end-of-maturity.
    :type interest: float

    :param volatility: The volatility of the underlying stock.
    :type volatility: float

    :param dividend_yield: The dividend yield of the underlying stock.
    :type dividend_yield: float

    :param steps: The number of steps in the binomial tree model.
    :type steps: int
    """

    def __init__(self, option_type: OptionType,
                 current_stock_price: float,
                 strike_price: float,
                 interest: float,
                 volatility: float,
                 dividend_yield: float,
                 steps: int):
        super().__init__(option_type,
                         current_stock_price,
                         strike_price,
                         interest, volatility,
                         dividend_yield,
                         steps)
        self.cached_price_tree = None
        self.cached_payoff_tree = None

    def price(self) -> float:
        """
        Calculate the price of the American option.

        :return: The price of the American option.
        :rtype: float
        """
        stock_price_tree = self.forward()
        payoff_tree = self.backward(stock_price_tree)
        return payoff_tree[0][0]

    def delta(self) -> float:
        """
        Calculate the delta of the American option.

        :return: The delta of the American option.
        :rtype: float
        """
        stock_price_tree = self.forward()
        payoff_tree = self.backward(stock_price_tree)
        c_u = payoff_tree[1][0]
        c_d = payoff_tree[1][1]
        s_u = self.current_stock_price * self._compound() * self._uncertainty()
        s_d = self.current_stock_price * self._compound() / self._uncertainty()
        return (c_u - c_d) / (s_u - s_d)

    def vega(self, delta_sigma: float = 0.01) -> float:
        """
        Calculate the vega of the American option.

        :param delta_sigma: The change in volatility for vega calculation, defaults to 1%.
        :type delta_sigma: float, optional

        :return: The vega of the American option.
        :rtype: float
        """
        original_price = self.price()

        sim_option = AmericanOption(self.option_type,
                                    self.current_stock_price,
                                    self.strike_price,
                                    self.interest,
                                    self.volatility * (1 + delta_sigma),
                                    self.dividend_yield,
                                    self.steps)
        sim_price = sim_option.price()

        return (sim_price - original_price) / delta_sigma

    def forward(self) -> list[list[float]]:
        """
        Build the binomial tree for stock prices.

        :return: A binomial tree representing future stock prices.
        :rtype: list[list[float]]
        """
        if self.cached_price_tree is not None:
            return self.cached_price_tree

        tree = [[self.current_stock_price]]

        for i in range(self.steps - 1):
            tree.append([])
            for previous_node in tree[i]:
                s_u = previous_node * self._compound() * self._uncertainty()
                s_d = previous_node * self._compound() / self._uncertainty()

                tree[i + 1].append(s_u)
                tree[i + 1].append(s_d)

        self.cached_price_tree = tree
        return tree

    def backward(self, price_tree: list[list[float]]) -> list[list[float]]:
        """
        Calculate the option price tree, according to the stock price binomial tree.

        :param price_tree: The binomial tree of stock prices.
        :type price_tree: list[list[float]]

        :return: A binomial tree representing option payoffs.
        :rtype: list[list[float]]
        """
        if self.cached_payoff_tree is not None:
            return self.cached_payoff_tree

        # instantiate tree with same number of levels as price_tree
        payoff_tree = [[] for i in range(len(price_tree))]

        # instantiate last level of payoffs (at time S_T)
        for j in range(len(price_tree[-1])):
            payoff_tree[-1].append(self._payoff(price_tree[-1][j]))

        # work backwards in the tree until the root
        # for each level of the tree starting from the level before the leaves
        # (the leaves were calculated above)
        for i in range(self.steps - 2, -1, -1):
            # for each node in the level
            for j in range(len(price_tree[i])):
                payoff = self._american_payoff(stock_price=price_tree[i][j],
                                               up_state_price=payoff_tree[i + 1][2 * j],
                                               down_state_price=payoff_tree[i + 1][2 * j + 1])
                payoff_tree[i].append(payoff)

        self.cached_payoff_tree = payoff_tree
        return payoff_tree

    def _american_payoff(self, stock_price: float, up_state_price: float, down_state_price: float) -> float:
        """
        Calculate the payoff of the American option at a given node in the binomial tree.
        This method is different from the protected _payoff() method, since it additionally checks whether
         it's worth it to exercise the option at each node.

        :param stock_price: The stock price at the current node.
        :type stock_price: float

        :param up_state_price: The option payoff in the up state.
        :type up_state_price: float

        :param down_state_price: The option payoff in the down state.
        :type down_state_price: float

        :return: The payoff of the American option at the current node.
        :rtype: float
        """
        u = self._compound() * self._uncertainty()
        d = self._compound() / self._uncertainty()
        p = (self._compound() - d) / (u - d)

        hold_payoff = exp(-self.interest * (1 / self.steps)) * (p * up_state_price + (1 - p) * down_state_price)
        exercise_payoff = self._payoff(stock_price)
        return max(hold_payoff, exercise_payoff)

    def _compound(self) -> float:
        """
        Calculate the compound factor for the binomial tree.

        :return: The compound factor.
        :rtype: float
        """
        return exp((self.interest - self.dividend_yield) * (1 / self.steps))

    def _uncertainty(self) -> float:
        """
        Calculate the uncertainty factor for the binomial tree.

        :return: The uncertainty factor.
        :rtype: float
        """
        return exp(self.volatility * sqrt((1 / self.steps)))


class EuropeanOption(Option):
    """
    Class for European options.

    :param option_type: The type of the option (CALL or PUT).
    :type option_type: OptionType

    :param current_stock_price: The current price of the underlying stock.
    :type current_stock_price: float

    :param strike_price: The strike price of the option.
    :type strike_price: float

    :param interest: The risk-free interest rate from now until end-of-maturity.
    :type interest: float

    :param volatility: The volatility of the underlying stock.
    :type volatility: float

    :param dividend_yield: The dividend yield of the underlying stock.
    :type dividend_yield: float

    :param steps: The number of random scenarios in the Monte Carlo simulation.
    :type steps: int

    :param time_period: The time period for the option, defaults to 0.5.
    :type time_period: float, optional
    """

    def __init__(self, option_type: OptionType,
                 current_stock_price: float,
                 strike_price: float,
                 interest: float,
                 volatility: float,
                 dividend_yield: float,
                 steps: int,
                 time_period: float = 0.5):
        super().__init__(option_type, current_stock_price, strike_price, interest, volatility, dividend_yield, steps)
        self.time_period = time_period

    def price(self) -> float:
        """
        Calculate the price of the European option using a Monte Carlo simulation.

        :return: The price of the European option.
        :rtype: float
        """
        sum_payoffs = 0

        for i in range(self.steps):
            rand_price = self._calculate_stock_price(random.gauss(mu=0, sigma=1))
            discounted_price = self._discount(rand_price)
            payoff = self._payoff(discounted_price)
            sum_payoffs += payoff

        return sum_payoffs / self.steps

    def _calculate_stock_price(self, epsilon: float) -> float:
        """
        Calculate the stock price for the European option using a random variable.

        :param epsilon: A random number sampled from a normal distribution with mean 0 and standard deviation 1.
        :type epsilon: float

        :return: The calculated stock price.
        :rtype: float
        """
        return exp((self.interest - self.dividend_yield - 1 / 2 * self.volatility ** 2) * self.time_period +
                   epsilon * self.volatility * sqrt(self.time_period)) * self.current_stock_price

    def _discount(self, asset_price: float) -> float:
        """
        Discount the asset price to the present value.

        :param asset_price: The price of the asset.
        :type asset_price: float

        :return: The discounted asset price.
        :rtype: float
        """
        return exp(-self.interest * self.time_period) * asset_price
