import pandas as pd


class CurrencyTrade:

    def __init__(self, starting_currency: str, intermediate_currency: str, arbitrage_rate: float, direct_rate: float):
        self.starting_currency = starting_currency
        self.intermediate_currency = intermediate_currency
        self.arbitrage_rate = arbitrage_rate
        self.direct_rate = direct_rate

    def __str__(self):
        return f"{self.starting_currency}->{self.intermediate_currency}: "\
               f"Arbitrage: {self.arbitrage_rate:.4f} vs Direct: {self.direct_rate}"


def exchange_rate(quot_matrix: pd.DataFrame, from_currency: str, to_currency: str) -> float:
    # in pd dataframes access to the matrix is column-first, row-second
    # so to access the 2nd element of the first row we need to type A[2][1]
    return quot_matrix[to_currency][from_currency]


def triangular_trade(starting_currency: str, intermediate_currency: str, quot_matrix: pd.DataFrame) -> float:
    start_to_interm = exchange_rate(quot_matrix,
                                    from_currency=starting_currency,
                                    to_currency=intermediate_currency)
    interm_to_end = start_to_interm * exchange_rate(quot_matrix,
                                                    from_currency=intermediate_currency,
                                                    to_currency=starting_currency)
    return interm_to_end


def check_all_triangular(starting_currency: str, quot_matrix: pd.DataFrame) -> list[tuple[str, str, float]]:
    trades = []

    for intermediate_currency in quot_matrix.columns:
        if starting_currency != intermediate_currency:
            triangular_rate = triangular_trade(starting_currency, intermediate_currency, quot_matrix)
            direct_rate = exchange_rate(quot_matrix,
                                        from_currency=intermediate_currency,
                                        to_currency=starting_currency)
            res = CurrencyTrade(starting_currency=starting_currency,
                                intermediate_currency=intermediate_currency,
                                arbitrage_rate=triangular_rate,
                                direct_rate=direct_rate)
            trades.append(res)

    return trades


DATA_PATH = "data/Quotation Matrix.xlsx"

quot_mat = pd.read_excel(DATA_PATH, index_col=0)
triangular_trades = check_all_triangular("USD", quot_mat)
print("\n".join([str(trade) for trade in triangular_trades]))
