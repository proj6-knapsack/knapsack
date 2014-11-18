import random

def random_color():
    """
    Generate a random color.
    :return: 3-tuple of rgb values normalized 0-1 as matplotlib likes
    """
    r = random.randint(1, 100)
    g = random.randint(1, 100)
    b = random.randint(1, 100)
    color = (r*0.01, g*0.01, b*0.01)
    return color




# find configuration with maximized value
def find_best_config(population):

    best_config = None
    max_value = None

    for x in population:
        if x.total_value > max_value:
            max_value = x.total_value
            best_config = x

    return best_config