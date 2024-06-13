import option_lib

CURRENT_STOCK_PRICE = 20
VOLATILITY = 0.35
INTEREST = 0.0298
DIVIDEND_YIELD = 0.015
EXPIRY_MONTHS = 6
STEPS = 100


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
    print("American Call price: ", american_call.calculate_price())
    print("American Put price: ", american_put.calculate_price())


if __name__ == "__main__":
    main()
