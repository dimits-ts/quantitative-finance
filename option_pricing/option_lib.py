import enum
import abc
from math import exp, sqrt


class OptionType(enum.Enum):
    CALL = "call"
    PUT = "put"


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
    def calculate_price(self) -> float:
        return 0


class AmericanOption(Option):

    def __init__(self, option_type: OptionType,
                 current_stock_price: float,
                 strike_price: float,
                 interest: float,
                 volatility: float,
                 dividend_yield: float,
                 expiry_months: int):
        super().__init__(option_type,
                         current_stock_price,
                         strike_price,
                         interest, volatility,
                         dividend_yield,
                         expiry_months)

    def compound(self):
        return exp((self.interest - self.dividend_yield) * (1 / self.steps))

    def uncertainty(self):
        return exp(self.volatility * sqrt((1 / self.steps)))

    def calculate_price(self) -> float:
        payoff_tree = self.forward()
        price_tree = self.backward(payoff_tree)
        return price_tree[0]

    def forward(self):
        tree = [self.current_stock_price]

        for i in range(self.steps):
            tree[i + 1] = []
            for previous_node in tree[i]:
                u = self.compound() * self.uncertainty()
                d = self.compound() / self.uncertainty()
                future_value = previous_node * self.compound()

                tree[i + 1].append(u * future_value)
                tree[i + 2].append(d * future_value)

        return tree

    def backward(self, price_tree: list[list[float]]) -> list[list[float]]:
        payoff_tree = []

        # instantiate last level of payoffs (at time S_T)
        for j in range(len(price_tree[-1])):
            payoff_tree.append(self.exercise_payoff(price_tree[-1][j]))

        # work backwards in the tree until the root
        for i in range(self.steps, 0, -1):
            payoff_tree[i] = []
            for j in range(payoff_tree[i - 1]):
                payoff = self.payoff(stock_price=price_tree[i - 1][j],
                                     up_state_price=payoff_tree[i][2 * j],
                                     down_state_price=payoff_tree[i][2 * j + 1])
                payoff_tree[i - 1].append(payoff)

        return payoff_tree

    def payoff(self, stock_price: float, up_state_price: float, down_state_price: float) -> float:
        u = self.compound() * self.uncertainty()
        d = self.compound() / self.uncertainty()
        p = (self.compound() - d) / (u - d)

        hold_payoff = exp(-self.interest * (1 / self.steps)) * (p * up_state_price + (1 - p) * down_state_price)
        exercise_payoff = self.exercise_payoff(stock_price)
        return max(hold_payoff, exercise_payoff)

    def exercise_payoff(self, stock_price):
        if self.option_type == OptionType.CALL:
            return max(0, stock_price - self.strike_price)
        elif self.option_type == OptionType.PUT:
            return max(0, self.strike_price - stock_price)
