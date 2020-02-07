import random
from statistics import stdev, median

# What you started with
start_wheels = 19
# Amount of currency you got
reward_threshold = 93

currency_result = []
i = 0
while True:
    i += 1
    wheels = start_wheels
    currency = 0

    while wheels > 0:
        wheels -= 1
        rnd = random.uniform(0.0, 3.0)
        if rnd < 1.0:
            wheels += 3
        else:
            currency += 3

    currency_result.append(currency)

    if (i > 10):
        avg = sum(currency_result) / len(currency_result)
        print("\nCurrency (iteration {}):".format(i))
        print("  Median: {}".format(median(currency_result)))
        print("  Average: {}".format(avg))
        print("  Min: {}".format(min(currency_result)))
        print("  Max: {}".format(max(currency_result)))
        print("  Std Deviation: {}".format(stdev(currency_result)))

        at_or_below = 0
        for result in currency_result:
            if result <= reward_threshold:
                at_or_below += 1
        print("  Percentile: {}".format(at_or_below/len(currency_result)))

