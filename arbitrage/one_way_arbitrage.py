import pandas as pd
import os
import sys

from fx_trades import exchange_rate, CurrencyTrade, trade_list_to_str


class OnewayTrade(CurrencyTrade):
    """
    A class implementing the CurrencyTrade abstract class, which describes a one-way arbitrage trade.
    """
    def __init__(self, starting_currency: str,
                 intermediate_currency: str,
                 end_currency: str,
                 arbitrage_rate: float,
                 quot_matrix: pd.DataFrame):
        self.quot_matrix = quot_matrix
        super().__init__(starting_currency, intermediate_currency, end_currency, arbitrage_rate)

    def is_successful(self):
        """
        Checks whether the arbitrage would be successful by comparing its rate to the standard, direct exchange rate.
        :return: true if arbitrage is possible
        """
        return self.arbitrage_rate > exchange_rate(self.quot_matrix,
                                                   from_currency=self.starting_currency,
                                                   to_currency=self.end_currency)

    def __str__(self):
        return f"{self.starting_currency}->{self.intermediate_currency}->{self.end_currency}" \
               f": {self.arbitrage_rate:.4f}"


def one_way_trade(starting_currency: str, intermediate_currency: str, end_currency: str,
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
    return start_to_interm * interm_to_end


def check_all_one_ways(starting_currency: str, end_currency: str, quot_matrix: pd.DataFrame) -> list[CurrencyTrade]:
    """
    Check all possible one-way trades for a given starting currency.

    :param starting_currency: The currency to start with.
    :type starting_currency: str
    :param end_currency: The final currency after the trade.
    :type end_currency: str
    :param quot_matrix: The quotation matrix containing exchange rates.
    :type quot_matrix: pd.DataFrame
    :return: A list of CurrencyTrade instances representing all possible triangular trades.
    :rtype: list[CurrencyTrade]
    """
    trades = []

    for intermediate_currency in quot_matrix.columns:
        if (end_currency != starting_currency and
                end_currency != intermediate_currency
                and starting_currency != intermediate_currency):
            one_way_rate = one_way_trade(starting_currency=starting_currency,
                                         intermediate_currency=intermediate_currency,
                                         end_currency=end_currency,
                                         quot_matrix=quot_matrix)

            res = OnewayTrade(starting_currency=starting_currency,
                              intermediate_currency=intermediate_currency,
                              end_currency=end_currency,
                              arbitrage_rate=one_way_rate,
                              quot_matrix=quot_matrix)

            trades.append(res)

    return trades


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <data_path> <starting_currency> <end_currency>")
        print("Example: python script.py 'data/Quotation Matrix.xlsx' 'USD' 'GBP'")
        sys.exit(1)

    data_path = sys.argv[1]
    starting_currency = sys.argv[2]
    end_currency = sys.argv[3]

    if not os.path.exists(data_path):
        print(f"Error: The file '{data_path}' does not exist.")
        sys.exit(1)

    try:
        quot_mat = pd.read_excel(data_path, index_col=0)
    except Exception as e:
        print(f"Error: Unable to read the file '{data_path}'.")
        print(f"Exception: {e}")
        sys.exit(1)

    if starting_currency not in quot_mat.index or end_currency not in quot_mat.columns:
        print(f"Error: The currency pair '{starting_currency}' to '{end_currency}' is not in the quotation matrix.")
        sys.exit(1)

    one_way_trades = check_all_one_ways(starting_currency=starting_currency,
                                        end_currency=end_currency,
                                        quot_matrix=quot_mat)
    print("All one-way arbitrage trades:")
    print(trade_list_to_str(one_way_trades))

    successful_one_ways = [trade for trade in one_way_trades if trade.is_successful()]
    print("Successful arbitrage trades:")
    print(trade_list_to_str(successful_one_ways))


if __name__ == "__main__":
    main()
