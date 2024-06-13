import enum
import abc
import random
from math import exp, sqrt


class OptionType(enum.Enum):
    CALL = enum.auto()
    PUT = enum.auto()


class Option(abc.ABC):

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
        return 0

    def _payoff(self, stock_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0., stock_price - self.strike_price)
        elif self.option_type == OptionType.PUT:
            return max(0., self.strike_price - stock_price)


class AmericanOption(Option):

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
        price_tree = self.forward()
        payoff_tree = self.backward(price_tree)
        return payoff_tree[0][0]

    def delta(self) -> float:
        price_tree = self.forward()
        payoff_tree = self.backward(price_tree)
        delta_u = self._stock_delta(payoff_up=payoff_tree[2][0], payoff_down=payoff_tree[2][1])
        delta_d = self._stock_delta(payoff_up=payoff_tree[2][2], payoff_down=payoff_tree[2][3])
        return (delta_u - delta_d) / (price_tree[1][0] - price_tree[1][1])

    def vega(self, delta_sigma: float = 0.01) -> float:
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
        if self.cached_price_tree is not None:
            return self.cached_price_tree

        tree = [[self.current_stock_price]]

        for i in range(self.steps - 1):
            tree.append([])
            for previous_node in tree[i]:
                u = self.compound() * self.uncertainty()
                d = self.compound() / self.uncertainty()
                future_value = previous_node * self.compound()

                tree[i + 1].append(u * future_value)
                tree[i + 1].append(d * future_value)

        self.cached_price_tree = tree
        return tree

    def backward(self, price_tree: list[list[float]]) -> list[list[float]]:
        if self.cached_payoff_tree is not None:
            return self.cached_payoff_tree

        # instantiate tree with same number of levels as price_tree
        payoff_tree = [[] for i in range(len(price_tree))]

        # instantiate last level of payoffs (at time S_T)
        for j in range(len(price_tree[-1])):
            payoff_tree[-1].append(self.exercise_payoff(price_tree[-1][j]))

        # work backwards in the tree until the root
        # for each level of the tree starting from the level before the leaves
        # (the leaves were calculated above)
        for i in range(self.steps - 2, -1, -1):
            # for each node in the level
            for j in range(len(price_tree[i])):
                payoff = self.american_payoff(stock_price=price_tree[i][j],
                                              up_state_price=payoff_tree[i + 1][2 * j],
                                              down_state_price=payoff_tree[i + 1][2 * j + 1])
                payoff_tree[i].append(payoff)

        self.cached_payoff_tree = payoff_tree
        return payoff_tree

    def american_payoff(self, stock_price: float, up_state_price: float, down_state_price: float) -> float:
        u = self.compound() * self.uncertainty()
        d = self.compound() / self.uncertainty()
        p = (self.compound() - d) / (u - d)

        hold_payoff = exp(-self.interest * (1 / self.steps)) * (p * up_state_price + (1 - p) * down_state_price)
        exercise_payoff = self._payoff(stock_price)
        return max(hold_payoff, exercise_payoff)

    def exercise_payoff(self, stock_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0., stock_price - self.strike_price)
        elif self.option_type == OptionType.PUT:
            return max(0., self.strike_price - stock_price)

    def compound(self):
        return exp((self.interest - self.dividend_yield) * (1 / self.steps))

    def uncertainty(self):
        return exp(self.volatility * sqrt((1 / self.steps)))

    def _stock_delta(self, payoff_up: float, payoff_down: float) -> float:
        u = self.compound() * self.uncertainty()
        d = self.compound() / self.uncertainty()
        return exp(-self.dividend_yield / self.steps) \
            * ((payoff_up - payoff_down) / (self.current_stock_price * (u - d)))


class EuropeanOption(Option):

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
        # this would be miles better in terms of performance with numpy,
        # but I'm keeping dependencies to 0 in this project
        sum_payoffs = 0

        for i in range(self.steps):
            rand_price = self._calculate_stock_price(random.gauss(mu=0, sigma=1))
            discounted_price = self._discount(rand_price)
            payoff = self._payoff(discounted_price)
            sum_payoffs += payoff

        return sum_payoffs / self.steps

    def _calculate_stock_price(self, epsilon: float) -> float:
        return exp((self.interest - self.dividend_yield - 1 / 2 * self.volatility ** 2) * self.time_period +
                   epsilon * self.volatility * sqrt(self.time_period)) * self.current_stock_price

    def _discount(self, asset_price: float) -> float:
        return exp(-self.interest * self.time_period) * asset_price
