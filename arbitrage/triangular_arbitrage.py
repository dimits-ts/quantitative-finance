import pandas as pd


class CurrencyTrade:

    def __init__(self, starting_currency: str, intermediate_currency: str, end_currency: str, arbitrage_rate: float):
        self.starting_currency = starting_currency
        self.intermediate_currency = intermediate_currency
        self.end_currency = end_currency
        self.arbitrage_rate = arbitrage_rate

    def __str__(self):
        return f"{self.starting_currency}->{self.intermediate_currency}->{self.end_currency}: " \
               f"Arbitrage rate: {self.arbitrage_rate:.4f}"


def exchange_rate(quot_matrix: pd.DataFrame, from_currency: str, to_currency: str) -> float:
    return quot_matrix.loc[from_currency, to_currency]


def triangular_trade(starting_currency: str, intermediate_currency: str, end_currency: str,
                     quot_matrix: pd.DataFrame) -> float:
    start_to_interm = exchange_rate(quot_matrix, from_currency=starting_currency, to_currency=intermediate_currency)
    interm_to_end = exchange_rate(quot_matrix, from_currency=intermediate_currency, to_currency=end_currency)
    end_to_start = exchange_rate(quot_matrix, from_currency=end_currency, to_currency=starting_currency)
    return start_to_interm * interm_to_end * end_to_start


def check_all_triangular(starting_currency: str, quot_matrix: pd.DataFrame) -> list[CurrencyTrade]:
    trades = []

    for intermediate_currency in quot_matrix.columns:
        for end_currency in quot_matrix.columns:
            if (end_currency != starting_currency and
                    end_currency != intermediate_currency and
                    starting_currency != intermediate_currency):
                triangular_rate = triangular_trade(starting_currency,
                                                   intermediate_currency,
                                                   end_currency,
                                                   quot_matrix)

                res = CurrencyTrade(starting_currency=starting_currency,
                                    intermediate_currency=intermediate_currency,
                                    end_currency=end_currency,
                                    arbitrage_rate=triangular_rate)

                trades.append(res)

    return trades


def filter_successful_arbitrages(currency_trades: list[CurrencyTrade]) -> list[CurrencyTrade]:
    return [trade for trade in currency_trades if trade.arbitrage_rate > 1]


DATA_PATH = "data/Quotation Matrix.xlsx"

quot_mat = pd.read_excel(DATA_PATH, index_col=0)
triangular_trades = check_all_triangular("USD", quot_mat)
print("All trades:")
print("\n".join([str(trade) for trade in triangular_trades]))
print("Arbitrage trades:")
print("\n".join([str(trade) for trade in filter_successful_arbitrages(triangular_trades)]))
