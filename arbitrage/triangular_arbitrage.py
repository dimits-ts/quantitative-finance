import pandas as pd
import os
import sys


class CurrencyTrade:
    """
    A record class to represent a currency trade.

    :param starting_currency: The currency to start with.
    :type starting_currency: str
    :param intermediate_currency: The currency to exchange to first.
    :type intermediate_currency: str
    :param end_currency: The final currency after the trade.
    :type end_currency: str
    :param arbitrage_rate: The arbitrage rate of the trade.
    :type arbitrage_rate: float
    """

    def __init__(self, starting_currency: str, intermediate_currency: str, end_currency: str, arbitrage_rate: float):
        """
        Initialize a CurrencyTrade record.

        :param starting_currency: The currency to start with.
        :type starting_currency: str
        :param intermediate_currency: The currency to exchange to first.
        :type intermediate_currency: str
        :param end_currency: The final currency after the trade.
        :type end_currency: str
        :param arbitrage_rate: The arbitrage rate of the trade.
        :type arbitrage_rate: float
        """
        self.starting_currency = starting_currency
        self.intermediate_currency = intermediate_currency
        self.end_currency = end_currency
        self.arbitrage_rate = arbitrage_rate

    def __str__(self):
        return f"{self.starting_currency}->{self.intermediate_currency}->{self.end_currency}: " \
               f"Arbitrage rate: {self.arbitrage_rate:.4f}"


def exchange_rate(quot_matrix: pd.DataFrame, from_currency: str, to_currency: str) -> float:
    """
    Get the exchange rate between two currencies.

    :param quot_matrix: The quotation matrix containing exchange rates.
    :type quot_matrix: pd.DataFrame
    :param from_currency: The currency to exchange from.
    :type from_currency: str
    :param to_currency: The currency to exchange to.
    :type to_currency: str
    :return: The exchange rate from `from_currency` to `to_currency`.
    :rtype: float
    """
    return quot_matrix.loc[from_currency, to_currency]


def triangular_trade(starting_currency: str, intermediate_currency: str, end_currency: str,
                     quot_matrix: pd.DataFrame) -> float:
    """
    Compute the triangular trade rate for a set of three currencies.

    :param starting_currency: The currency to start with.
    :type starting_currency: str
    :param intermediate_currency: The currency to exchange to first.
    :type intermediate_currency: str
    :param end_currency: The final currency after the trade.
    :type end_currency: str
    :param quot_matrix: The quotation matrix containing exchange rates.
    :type quot_matrix: pd.DataFrame
    :return: The return in starting currency, for 1 monetary unit of starting currency, after the trade
    :rtype: float
    """
    start_to_interm = exchange_rate(quot_matrix, from_currency=starting_currency, to_currency=intermediate_currency)
    interm_to_end = exchange_rate(quot_matrix, from_currency=intermediate_currency, to_currency=end_currency)
    end_to_start = exchange_rate(quot_matrix, from_currency=end_currency, to_currency=starting_currency)
    return start_to_interm * interm_to_end * end_to_start


def check_all_triangular(starting_currency: str, quot_matrix: pd.DataFrame) -> list[CurrencyTrade]:
    """
    Check all possible triangular trades for a given starting currency.

    :param starting_currency: The currency to start with.
    :type starting_currency: str
    :param quot_matrix: The quotation matrix containing exchange rates.
    :type quot_matrix: pd.DataFrame
    :return: A list of CurrencyTrade instances representing all possible triangular trades.
    :rtype: list[CurrencyTrade]
    """
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
    """
    Filter the list of currency trades to find successful arbitrages.

    :param currency_trades: A list of CurrencyTrade instances.
    :type currency_trades: list[CurrencyTrade]
    :return: A list of CurrencyTrade instances with an arbitrage rate greater than 1.
    :rtype: list[CurrencyTrade]
    """
    return [trade for trade in currency_trades if trade.arbitrage_rate > 1]


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <data_path> <starting_currency>")
        print("Example: python script.py 'data/Quotation Matrix.xlsx' 'USD'")
        sys.exit(1)

    data_path = sys.argv[1]
    starting_currency = sys.argv[2]

    if not os.path.exists(data_path):
        print(f"Error: The file '{data_path}' does not exist.")
        sys.exit(1)

    try:
        quot_mat = pd.read_excel(data_path, index_col=0)
    except Exception as e:
        print(f"Error: Unable to read the file '{data_path}'.")
        print(f"Exception: {e}")
        sys.exit(1)

    if starting_currency not in quot_mat.index:
        print(f"Error: The starting currency '{starting_currency}' is not in the quotation matrix.")
        sys.exit(1)

    triangular_trades = check_all_triangular(starting_currency, quot_mat)
    successful_trades = filter_successful_arbitrages(triangular_trades)
    print("Arbitrage trades:")
    print("\n".join([str(trade) for trade in successful_trades]))


if __name__ == "__main__":
    main()
