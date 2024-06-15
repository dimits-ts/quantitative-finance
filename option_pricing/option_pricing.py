import option_lib
import random

CURRENT_STOCK_PRICE = 20
VOLATILITY = 0.35
# bi-annual interest instead of given annual interest
INTEREST = 0.0298
DIVIDEND_YIELD = 0.015
EXPIRY_YEARS = 0.5
AMERICAN_STEPS = 15
EUROPEAN_STEPS = 10000
SEED = 42


def main():
    random.seed(SEED)
    # strike price = forward price
    strike_price = CURRENT_STOCK_PRICE * (1 + INTEREST)

    american_call = option_lib.AmericanOption(option_lib.OptionType.CALL,
                                              current_stock_price=CURRENT_STOCK_PRICE,
                                              strike_price=strike_price,
                                              interest=INTEREST,
                                              volatility=VOLATILITY,
                                              dividend_yield=DIVIDEND_YIELD,
                                              steps=AMERICAN_STEPS)
    american_call_price = american_call.price()
    american_call_delta = american_call.delta()
    american_call_vega = american_call.vega()

    print(f"American Call Price: {american_call_price}, Delta: {american_call_delta}, Vega: {american_call_vega}")

    american_put = option_lib.AmericanOption(option_lib.OptionType.PUT,
                                             current_stock_price=CURRENT_STOCK_PRICE,
                                             strike_price=strike_price,
                                             interest=INTEREST,
                                             volatility=VOLATILITY,
                                             dividend_yield=DIVIDEND_YIELD,
                                             steps=AMERICAN_STEPS)

    american_put_price = american_put.price()
    american_put_delta = american_put.delta()
    american_put_vega = american_put.vega()

    print(f"American Put Price: {american_put_price}, Delta: {american_put_delta}, Vega: {american_put_vega}")

    european_call = option_lib.EuropeanOption(option_lib.OptionType.CALL,
                                              current_stock_price=CURRENT_STOCK_PRICE,
                                              strike_price=strike_price,
                                              interest=INTEREST,
                                              volatility=VOLATILITY,
                                              dividend_yield=DIVIDEND_YIELD,
                                              steps=EUROPEAN_STEPS,
                                              time_period=EXPIRY_YEARS)
    european_call_price = european_call.price()
    print("European Call Price: ", european_call_price)

    european_put = option_lib.EuropeanOption(option_lib.OptionType.PUT,
                                             current_stock_price=CURRENT_STOCK_PRICE,
                                             strike_price=strike_price,
                                             interest=INTEREST,
                                             volatility=VOLATILITY,
                                             dividend_yield=DIVIDEND_YIELD,
                                             steps=EUROPEAN_STEPS,
                                             time_period=EXPIRY_YEARS)
    european_put_price = european_put.price()
    print("European Call Price: ", european_put_price)

    print("Check: European options must be cheaper than American:",
          american_call_price > european_call_price and american_put_price > european_put_price)

    # allow some margin for floating point errors
    print(f"Check: Call Delta - Put Delta ~= 1: Result=", american_call_delta - american_put_delta)


if __name__ == "__main__":
    main()
