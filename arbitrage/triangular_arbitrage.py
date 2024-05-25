import pandas as pd
import os
import sys

from fx_trades import exchange_rate, CurrencyTrade, trade_list_to_str


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


def filter_successful_triangular(currency_trades: list[CurrencyTrade]) -> list[CurrencyTrade]:
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
    print("All trades:")
    print(trade_list_to_str(triangular_trades))

    successful_trades = filter_successful_triangular(triangular_trades)
    print("Arbitrage trades:")
    print(trade_list_to_str(successful_trades))


if __name__ == "__main__":
    main()
