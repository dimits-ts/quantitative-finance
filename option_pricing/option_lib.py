import enum
import abc
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
    def calculate_price(self) -> float:
        return 0


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

    def calculate_price(self) -> float:
        price_tree = self.forward()
        payoff_tree = self.backward(price_tree)
        return payoff_tree[0][0]

    def forward(self):
        tree = [[self.current_stock_price]]

        for i in range(self.steps - 1):
            tree.append([])
            for previous_node in tree[i]:
                u = self.compound() * self.uncertainty()
                d = self.compound() / self.uncertainty()
                future_value = previous_node * self.compound()

                tree[i + 1].append(u * future_value)
                tree[i + 1].append(d * future_value)

        return tree

    def backward(self, price_tree: list[list[float]]) -> list[list[float]]:
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
                payoff = self.payoff(stock_price=price_tree[i][j],
                                     up_state_price=payoff_tree[i + 1][2 * j],
                                     down_state_price=payoff_tree[i + 1][2 * j + 1])
                payoff_tree[i].append(payoff)

        return payoff_tree

    def payoff(self, stock_price: float, up_state_price: float, down_state_price: float) -> float:
        u = self.compound() * self.uncertainty()
        d = self.compound() / self.uncertainty()
        p = (self.compound() - d) / (u - d)

        hold_payoff = exp(-self.interest * (1 / self.steps)) * (p * up_state_price + (1 - p) * down_state_price)
        exercise_payoff = self.exercise_payoff(stock_price)
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
