############################################################################
## Knapsack Problem:
## Given a number of objects n with weights w and value v,
## how can they be placed in a knapsack with capacity c
## as to minimize the total weight and maximize the total value within?
############################################################################

import random
import defs

# knapsack parameters
capacity = 50
num_boxes = 10
weight_max = 30
max_value = 10

# create a collection of n objects with weights w and values v to choose from
box_collection = list()

contents = list()

# weight and value parameters
for i in range(num_boxes):
    weight = random.randint(1, 30)
    value = random.randint(1, 10)
    box = defs.Box(i, weight, value)
    box_collection.append(box)

boxes_outside = box_collection[:]

# GA parameters
pop_size = 50
rounds = 100
crossover_rate = 0.9
mutation_rate = 0.1


population = list()
curr_size = 0

#create population of box configurations with weight <= capacity
while curr_size <= pop_size:

    curr_weight = 0
    curr_value = 0
    total_weight = 0
    total_value = 0

    while curr_weight <= capacity and len(boxes_outside) > 0:

        full_box_stats = list()
        #add a random box to the knapsack
        random_idx = random.randint(0, len(boxes_outside)-1)
        chosen_box = boxes_outside[random_idx]
        curr_weight += chosen_box.weight
        curr_value += chosen_box.value

        #add it to the contents
        contents.append(chosen_box)
        chosen_box.inside = True

        #check if there's any possible boxes to add to the contents without going over capacity
        for x in boxes_outside[:]:
            if x.weight + curr_weight > capacity:
                boxes_outside.remove(x)

    #create chromsome for population
    chromosome = list()
    for box in box_collection:
        if box.inside is True:
            chromosome.append(1)
            total_value += box.value
            total_weight += box.weight

        else:
            chromosome.append(0)

    full_box_stats = defs.BoxCollection(chromosome, total_weight, total_value)
    population.append(full_box_stats)
    curr_size += 1

    #reset knapsack
    boxes_outside = box_collection[:]
    for box in boxes_outside:
        box.inside = False


##################################
## Crossover function goes here
###################################


###################################
## Mutation function goes here
###################################

##################################
## WoC function goes here
##################################