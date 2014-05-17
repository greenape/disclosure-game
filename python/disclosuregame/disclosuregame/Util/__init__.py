__all__ = ["sqlite_dump", "sqlite_merge"]

from random import Random

def random_expectations(depth=0, breadth=3, low=1, high=10, random=Random()):
    """
    Generate depth x breadth array of random numbers where each row sums to
    high, with a minimum of low.
    """
    result = []
    if depth == 0:
        initial = high + 1
        for i in range(breadth - 1):
            n = random.randint(low, initial - (low * (breadth - i)))
            initial -= n
            result.append(n)
        result.append(initial - low)
        random.shuffle(result)
    else:
        result = [random_expectations(depth - 1, breadth, low, high, random) for x in range(breadth)]
    return result

def weighted_random_choice(choices, weights, random=Random()):
    population = [val for val, cnt in zip(choices, weights) for i in range(int(cnt))]
    return random.choice(population)

def shuffled(target, random=Random()):
    """
    Return a shuffled version of the argument
    """
    a = list(target)
    random.shuffle(a)
    return a