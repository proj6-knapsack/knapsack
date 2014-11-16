############################################################################
## Knapsack Problem:
## Given a number of objects n with weights w and value v,
## how can they be placed in a knapsack with capacity c
## as to minimize the total weight and maximize the total value within?
############################################################################

import random
import defs



def genetic_algorithm(capacity, num_boxes, weight_max, max_value):
    """
    :return: BoxCollection instance with optimal packing (greatest value and lowest weight)
    """

    # create a collection of n objects with weights w and values v to choose from
    box_collection = list()

    # keep track of the best collection found so far
    optimal_collection = None

    contents = list()

    ###############################
    # weight and value parameters
    ###############################

    for i in range(num_boxes):
        weight = random.randint(1, 30)
        value = random.randint(1, 10)
        box = defs.Box(i, weight, value)
        box_collection.append(box)

    boxes_outside = box_collection[:]

    ##################
    # GA parameters
    ##################
    pop_size = 50
    rounds = 100
    crossover_rate = 0.9
    mutation_rate = 0.1


    population = list()
    round_num = 0

    while round_num < rounds:

        print "Evolution Round", round_num
        round_num += 1

        curr_size = 0  # reset current size each evolution round
        while curr_size <= pop_size:
            curr_weight = 0
            curr_value = 0
            total_weight = 0
            total_value = 0

            #create population of box configurations with weight <= capacity
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

            full_box_stats = defs.BoxCollection(chromosome, total_weight, total_value, box_collection)
            population.append(full_box_stats)

            curr_size += 1

            #reset knapsack
            boxes_outside = box_collection[:]
            for box in boxes_outside:
                box.inside = False

            # print debug info about this population member
            print "\tPop Member {0}:\t{1}\tValue: {2}\tCost: {3}".format(
                curr_size, full_box_stats.box_stats, full_box_stats.total_value, full_box_stats.total_weight)

        ##################################
        ## Crossover function goes here
        ###################################

        ######################
        # mutation function
        ######################

        # perform mutation on weakest box config
        min_value = 99999999999999
        worst_box_config = None
        for x in population:
            if x.total_value < min_value:
                min_value = x.total_value
                worst_box_config = x

        print "\tMUTATING:\t{0}\tValue: {1}\tCost: {2}".format(worst_box_config.box_stats, worst_box_config.total_value, worst_box_config.total_weight)

        # mutate x elements at random indices
        num_to_switch = random.randint(0, 9)
        idx_to_switch = list()

        config_to_mutate = population.index(worst_box_config)

        while len(idx_to_switch) < num_to_switch:
            idx = random.randint(0, 9)
            if idx not in idx_to_switch:
                idx_to_switch.append(idx)

        x = population[config_to_mutate]
        for y in idx_to_switch:
            if x.box_stats[y] == 0:
                x.box_stats[y] = 1
            else:
                x.box_stats[y] = 0

        # have to recompute value and cost for mutated element
        x.update_values()

        print "\tNEW VALUE:\t{0}\tValue: {1}\tCost: {2}".format(x.box_stats, x.total_value, x.total_weight)


        # find and record best population member from this generation
        for x in population:
            if optimal_collection == None:
                optimal_collection = x
            elif (x.total_value > optimal_collection.total_value) and (x.total_weight < weight_max):
                optimal_collection = x

        print "\tBEST COLL.:\t{0}\tValue: {1}\tCost: {2}".format(optimal_collection.box_stats, optimal_collection.total_value, optimal_collection.total_weight)

    print "\tBEST COLL.:\t{0}\tValue: {1}\tCost: {2}".format(optimal_collection.box_stats, optimal_collection.total_value, optimal_collection.total_weight)



##################################
## WoC function goes here
##################################


def wisdom_of_crowds(crowd_size, population_size, mutation_rate, generations):
    pass




#######################
# knapsack parameters
#######################

capacity = 50
num_boxes = 10
weight_max = 30
max_value = 10

best = genetic_algorithm(capacity, num_boxes, weight_max, max_value)
