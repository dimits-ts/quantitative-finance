import pandas as pd
import os
import sys

from fx_trades import exchange_rate, CurrencyTrade, trade_list_to_str


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

            res = CurrencyTrade(starting_currency=starting_currency,
                                intermediate_currency=intermediate_currency,
                                end_currency=end_currency,
                                arbitrage_rate=one_way_rate)

            trades.append(res)

    return trades


def filter_successful_one_ways(currency_trades: list[CurrencyTrade], quot_matrix: pd.DataFrame) -> list[CurrencyTrade]:
    """
    Filter the list of currency trades to find successful one-way arbitrages.

    :param quot_matrix: The quotation matrix
    :param currency_trades: A list of CurrencyTrade instances.
    :type currency_trades: list[CurrencyTrade]
    :return: A list of CurrencyTrade instances with an arbitrage rate greater than 1.
    :rtype: list[CurrencyTrade]
    """
    return [trade for trade in currency_trades
            if trade.arbitrage_rate > exchange_rate(quot_matrix,
                                                    from_currency=trade.starting_currency,
                                                    to_currency=trade.end_currency)]


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

    arbitrage_trades = check_all_one_ways(starting_currency=starting_currency,
                                          end_currency=end_currency,
                                          quot_matrix=quot_mat)
    print("All one-way arbitrage trades:")
    print(trade_list_to_str(arbitrage_trades))

    successful_one_ways = filter_successful_one_ways(arbitrage_trades, quot_mat)
    print("Successful arbitrage trades:")
    print(trade_list_to_str(successful_one_ways))


if __name__ == "__main__":
    main()
