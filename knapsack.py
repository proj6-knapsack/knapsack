############################################################################
## Knapsack Problem:
## Given a number of objects n with weights w and value v,
## how can they be placed in a knapsack with capacity c
## as to maximize the total value within?
############################################################################

import random
import math
import defs


DEBUG_EVOLUTION = True
DEBUG_WOC = True


def genetic_algorithm(boxes, capacity, num_boxes, weight_max, population_size, generations):
    """
    :return: BoxCollection instance with optimal packing (greatest value and lowest weight)
    """

    # boxes are only created once, outside this function,
    # so that we are solving the same problem each time.
    # woc requires that there are multiple solutions to the same problem.
    box_collection = boxes
    boxes_outside = box_collection[:]

    # keep track of the best collection found so far
    optimal_collection = None

    contents = list()


    ##################
    # GA parameters
    ##################

    crossover_rate = 0.75
    num_to_crossover = math.ceil(population_size * crossover_rate)

    mutation_rate = 0.1
    num_to_mutate = math.ceil(population_size * mutation_rate)

    population = list()
    round_num = 0

    while round_num < generations:

        if DEBUG_EVOLUTION:
            print "Evolution Round", round_num
        round_num += 1

        curr_size = 0  # reset current size each evolution round
        while curr_size <= population_size:
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
            if DEBUG_EVOLUTION:
                print "\tPop Member {0}:\t{1}".format(curr_size, full_box_stats)

        ######################################
        # crossover function
        #######################################

        num_crossed = 0

        while num_crossed < num_to_crossover:
            # find top 2 box configs (those with the highest value)
            best_box_config = defs.find_best_config(population)

            population_minus_best = population[:]
            population_minus_best.remove(best_box_config)

            next_best_config = defs.find_best_config(population_minus_best)

            # perform crossover:
            # child's first half is from best config, second half from second best config
            child = list()

            #divide configs into 2 parts
            length = int(math.ceil(num_boxes/2))

            for x in best_box_config.box_stats[0:length]:
                child.append(x)
            for y in next_best_config.box_stats[length:num_boxes]:
                child.append(y)

            # find stats on child box config
            child_value = 0
            child_weight = 0

            for i in range(len(box_collection)):
                if child[i] == 1:
                    child_value += box_collection[i].value
                    child_weight += box_collection[i].weight

            child_box_config = defs.BoxCollection(child, child_weight, child_value, box_collection)

            # if total weight of child box config > capacity, remove boxes with low values
            sorted_by_value = sorted(box_collection, key=lambda box: box.value)

            box_idx = 0

            while child_weight > weight_max:
                least_value_box = sorted_by_value[box_idx]
                least_value_id = least_value_box.id

                if child_box_config.box_stats[least_value_id] == 1:
                    child_box_config.box_stats[least_value_id] = 0
                    child_weight = child_weight - least_value_box.weight
                else:
                    box_idx += 1

            num_crossed += 1

        # TODO: remove as many random box configs as there are new children


        ######################
        # mutation function
        ######################

        num_mutated = 0

        while num_mutated < num_to_mutate:
            # perform mutation on weakest box configs
            min_value = 99999999999999
            worst_box_config = None
            for x in population:
                if x.total_value < min_value:
                    min_value = x.total_value
                    worst_box_config = x

            if DEBUG_EVOLUTION:
                print "\tMUTATING:\t", worst_box_config

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

            if DEBUG_EVOLUTION:
                print "\tNEW VALUE:\t{1}".format(curr_size, x)


            # find and record best population member from this generation
            for x in population:
                if optimal_collection == None:
                    optimal_collection = x
                elif (x.total_value > optimal_collection.total_value) and (x.total_weight < weight_max):
                    optimal_collection = x

            num_mutated += 1

    if DEBUG_EVOLUTION:
        print "\tBEST COLL.:\t{0}".format(optimal_collection)

    return optimal_collection



def wisdom_of_crowds(boxes, crowd_size, capacity, num_boxes, weight_max, population_size, generations):

    best_solution = None

    for c in range(crowd_size):
        solution = genetic_algorithm(boxes, capacity, num_boxes, weight_max, population_size, generations)

        if DEBUG_WOC:
            print "CROWD SOLUTION", c, ":", solution

        if best_solution == None:
            best_solution = solution
        elif (solution.total_value > best_solution.total_value) and (solution.total_weight < weight_max):
            best_solution = solution

    return best_solution



def create_boxes(num_boxes, weight_max, value_max):
    # create a collection of n objects with weights w and values v to choose from
    boxes = list()
    for i in range(num_boxes):
        weight = random.randint(1, weight_max)
        value = random.randint(1, value_max)
        box = defs.Box(i, weight, value)
        boxes.append(box)
    return boxes




if __name__ == "__main__":

    #
    # genetic algorithm and WoC parameters
    #
    crowd_size = 3
    population_size = 5
    generations = 10


    #
    # knapsack parameters
    #
    capacity = 50
    num_boxes = 10
    weight_max = 30
    value_max = 30


    boxes = create_boxes(num_boxes, weight_max, value_max)

    best_solution = wisdom_of_crowds(boxes, crowd_size, capacity, num_boxes, weight_max, population_size, generations)

    print "FINAL RESULT:", best_solution