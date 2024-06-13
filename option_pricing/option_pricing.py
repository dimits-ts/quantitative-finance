import option_lib

CURRENT_STOCK_PRICE = 20
VOLATILITY = 0.35
INTEREST = 0.0298
DIVIDEND_YIELD = 0.015
EXPIRY_MONTHS = 6
STEPS = 10


def main():
    # strike price = forward price
    strike_price = CURRENT_STOCK_PRICE * (1 + INTEREST)
    american_call = option_lib.AmericanOption(option_lib.OptionType.CALL,
                                              current_stock_price=CURRENT_STOCK_PRICE,
                                              strike_price=strike_price,
                                              interest=INTEREST,
                                              volatility=VOLATILITY,
                                              dividend_yield=DIVIDEND_YIELD,
                                              steps=STEPS)

    american_put = option_lib.AmericanOption(option_lib.OptionType.PUT,
                                             current_stock_price=CURRENT_STOCK_PRICE,
                                             strike_price=strike_price,
                                             interest=INTEREST,
                                             volatility=VOLATILITY,
                                             dividend_yield=DIVIDEND_YIELD,
                                             steps=STEPS)
    print("American Call Price: ", american_call.price(),
          " Delta: ", american_call.delta(),
          " Vega:", american_call.vega())
    print("American Put Price: ", american_put.price(),
          " Delta: ", american_put.delta(),
          " Vega:", american_put.vega())


if __name__ == "__main__":
    main()
