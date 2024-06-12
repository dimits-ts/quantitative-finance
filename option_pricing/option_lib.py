import enum
import abc


class OptionType(enum.Enum):
    CALL = "call"
    PUT = "put"


class Option(abc.ABC):

    def __init__(self,
                 option_type: OptionType,
                 current_stock_price: float,
                 interest: float,
                 volatility: float,
                 dividend_yield: float,
                 expiry_months: int):
        self.expiry_months = expiry_months
        self.dividend_yield = dividend_yield
        self.volatility = volatility
        self.interest = interest
        self.current_stock_price = current_stock_price
        self.option_type = option_type

    @abc.abstractmethod
    def calculate_price(self) -> float:
        return 0


