import option_lib
import random

CURRENT_STOCK_PRICE = 20
VOLATILITY = 0.35
INTEREST = 0.0298
DIVIDEND_YIELD = 0.015
EXPIRY_MONTHS = 6
AMERICAN_STEPS = 10
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

    print("American Call Price: ", american_call.price(),
          " Delta: ", american_call.delta(),
          " Vega:", american_call.vega())

    american_put = option_lib.AmericanOption(option_lib.OptionType.PUT,
                                             current_stock_price=CURRENT_STOCK_PRICE,
                                             strike_price=strike_price,
                                             interest=INTEREST,
                                             volatility=VOLATILITY,
                                             dividend_yield=DIVIDEND_YIELD,
                                             steps=AMERICAN_STEPS)

    print("American Put Price: ", american_put.price(),
          " Delta: ", american_put.delta(),
          " Vega:", american_put.vega())

    european_call = option_lib.EuropeanOption(option_lib.OptionType.CALL,
                                              current_stock_price=CURRENT_STOCK_PRICE,
                                              strike_price=strike_price,
                                              interest=INTEREST,
                                              volatility=VOLATILITY,
                                              dividend_yield=DIVIDEND_YIELD,
                                              steps=EUROPEAN_STEPS)
    print("European Call Price: ", european_call.price())

    european_put = option_lib.EuropeanOption(option_lib.OptionType.PUT,
                                             current_stock_price=CURRENT_STOCK_PRICE,
                                             strike_price=strike_price,
                                             interest=INTEREST,
                                             volatility=VOLATILITY,
                                             dividend_yield=DIVIDEND_YIELD,
                                             steps=EUROPEAN_STEPS)
    print("European Put Price: ", european_put.price())


if __name__ == "__main__":
    main()
