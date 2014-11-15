############################################################################
## Knapsack Problem:
## Given a number of objects n with weights w and value v,
## how can they be placed in a knapsack with capacity c
## as to minimize the total weight and maximize the total value within?
############################################################################

import defs
import random

# knapsack parameters
capacity = 50
num_boxes = 10
weight_max = 30
max_value = 10

# create a collection of n objects with weights w and values v to choose from
collection = list()

contents = list()

# weight and value parameters
for i in range(num_boxes):
    weight = random.randint(1, 30)
    value = random.randint(1, 10)
    box = defs.Box(i, weight, value)
    collection.append(box)



####################################
## GA Parameters
####################################

population = 100
rounds = 100
crossover_rate = 0.9
mutation_rate = 0.1

## this is just an example of how to generate a population
## put boxes in the knapsack in a random configuration

curr_weight = 0
curr_value = 0

while curr_weight <= capacity and len(collection) > 0:

    #add a random box to the knapsack
    random_idx = random.randint(0, len(collection)-1)
    chosen_box = collection[random_idx]
    curr_weight += chosen_box.weight
    curr_value += chosen_box.value

    #add it to the contents
    contents.append(chosen_box)

    #remove from pool of possibilities
    collection.remove(chosen_box)

    #check if there's any possible boxes to add to the contents without going over capacity
    for x in collection[:]:
        if x.weight + curr_weight > capacity:
            collection.remove(x)

