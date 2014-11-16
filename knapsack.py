############################################################################
## Knapsack Problem:
## Given a number of objects n with weights w and value v,
## how can they be placed in a knapsack with capacity c
## as to maximize the total value within?
############################################################################

import random
import math
import defs
import matplotlib.pyplot as plt


DEBUG_EVOLUTION = False
DEBUG_WOC = True


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



def plot_ga_stats(data):

    N = len(data[0])
    ind = xrange(N)
    width = 1

    for crowd_member in data:
        costs = [x.total_value for x in crowd_member]
        p1 = plt.plot(ind, costs)
        color = random_color()
        p1[-1].set_color(color)

    plt.xlabel('Generations')
    plt.ylabel('Value')
    plt.grid(True)

    plt.xlim([0,N])

    plt.show()




def genetic_algorithm(boxes, capacity, num_boxes, weight_max, population_size, generations):
    """
    :return: tuple
    0: BoxCollection instance with optimal packing (greatest value and lowest weight)
    1: list of values for the best solution from each generation - used in stats
    """

    # boxes are only created once, outside this function,
    # so that we are solving the same problem each time.
    # woc requires that there are multiple solutions to the same problem.
    box_collection = boxes
    boxes_outside = box_collection[:]

    # keep track of the best collection found so far
    optimal_collection = None

    # list of boxes contained inside a configuration?
    contents = list()


    # list of lists that tracks stats over evolution
    performance_stats = list()  #  [[best_val, best_weight, avg_value, avg_weight],...]

    # remember the best solutions from each generation.
    best_of_each_generation = list()


    ##################
    # GA parameters
    ##################

    crossover_rate = 0.75
    num_to_crossover = math.ceil(population_size * crossover_rate)

    mutation_rate = 0.1
    num_to_mutate = math.ceil(population_size * mutation_rate)

    population = list()
    round_num = 0


    # evolve a solution through a number of generations
    while round_num < generations:

        if DEBUG_EVOLUTION:
            print "Evolution Generation #", round_num
        round_num += 1

        # build random initial population
        curr_size = 0  # have to reset current size each evolution round
        while curr_size <= population_size:
            curr_weight = 0
            curr_value = 0
            total_weight = 0
            total_value = 0

            # create population of random box configurations with weight <= capacity
            while curr_weight <= capacity and len(boxes_outside) > 0:

                #add a random box to the knapsack
                random_idx = random.randint(0, len(boxes_outside)-1)
                chosen_box = boxes_outside[random_idx]
                curr_weight += chosen_box.weight
                curr_value += chosen_box.value

                #add it to the contents
                contents.append(chosen_box)
                chosen_box.inside = True

                #check if there's any possible boxes to add to the contents without going over capacity
                # TODO: double check this actually adds the box to the contents
                for x in boxes_outside[:]:
                    if x.weight + curr_weight > capacity:
                        boxes_outside.remove(x)

            # create chromosome for population
            # calculate this collection's value and weight
            chromosome = list()
            for box in box_collection:
                if box.inside is True:
                    chromosome.append(1)
                    total_value += box.value
                    total_weight += box.weight
                else:
                    chromosome.append(0)

            # create BoxCollection from chromosome, add to population
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
            num_mutated += 1

            if DEBUG_EVOLUTION:
                print "\tNEW VALUE:\t{1}".format(curr_size, x)


        # END OF THIS GENERATION
        # find and record best population member from this generation
        for x in population:
            if optimal_collection == None:
                optimal_collection = x
            elif (x.total_value > optimal_collection.total_value) and (x.total_weight < weight_max):
                optimal_collection = x
        best_of_each_generation.append(optimal_collection)
        if DEBUG_EVOLUTION:
            print "\tBEST:\t\t{0}".format(optimal_collection)


    # END OF ALL GENERATIONS
    
    # for idx, s in enumerate(best_of_each_generation):
    #     print "Best Sol. Gen. {0}:\t{1}".format(idx, s)
    # generation_best_values = [x.total_value for x in best_of_each_generation]
    # plot_ga_stats(generation_best_values)


    return (optimal_collection, best_of_each_generation)





def wisdom_of_crowds(boxes, crowd_size, capacity, num_boxes, weight_max, population_size, generations):

    solutions = []
    best_solution = None
    ga_stats = [] # list of stats for each crowd member's evolution

    for c in range(crowd_size):
        print "\nCROWD #", c
        solution_tuple = genetic_algorithm(boxes, capacity, num_boxes, weight_max, population_size, generations)
        solution = solution_tuple[0]
        solutions.append(solution)
        ga_stats.append(solution_tuple[1])

        if DEBUG_WOC:
            print "CROWD SOLUTION", c, ":", solution

        if best_solution == None:
            best_solution = solution
        elif (solution.total_value > best_solution.total_value) and (solution.total_weight < weight_max):
            best_solution = solution


    # try to create even better solution by merging crowd's solutions
    # count which boxes are shared by the crowd
    shared_box_counts = [0 for x in range(num_boxes)]
    for idx, solution in enumerate(solutions):
        for idx in range(num_boxes):
            if solution.box_stats[idx] == 1:
                shared_box_counts[idx] += 1
    # print "SHARED BOXES:\n", shared_box_counts

    # create a new solution from boxes which are shared by the majority of the solutions
    threshold = 0.5 # percentage of crowd that must share this box for it to be considered for the new solution
    threshold_count = int(crowd_size * threshold)
    new_solution = [0 for x in range(num_boxes)]
    for idx, box in enumerate(shared_box_counts):
        if box >= threshold_count:
            new_solution[idx] = 1

    new_full_solution = defs.BoxCollection(new_solution, 0, 0, boxes)
    new_full_solution.update_values()
    # print "NEW FULL:", new_full_solution

    # if the box is over weight, remove objects until within weight
    while new_full_solution.total_weight > weight_max:
        # find box in solution with lowest value
        object_to_remove = None
        for idx in range(num_boxes):
            # if this box is included in the solution
            if new_full_solution.box_stats[idx] == 1:
                # and it's less valuable that the box we're planning to remove
                if object_to_remove == None or (boxes[idx].value < boxes[object_to_remove]):
                    # select this box instead
                    object_to_remove = idx

        # remove the selected box
        new_full_solution.box_stats[object_to_remove] = 0
        # recalculate total weight and value of the solution
        new_full_solution.update_values()

    # print "CORRECTED FULL:", new_full_solution

    # try to find any other boxes we can add while remaining within the weight limit
    # TODO: sort them by value so we will use the higher-value items first
    found = False
    idx = 0
    while not found and idx < num_boxes:
        if new_full_solution.box_stats[idx] == 0:
            new_weight = new_full_solution.total_weight + boxes[idx].weight
            if new_weight <= weight_max:
                new_full_solution.box_stats[idx] = 1
                new_full_solution.update_values()
                found = True
        idx += 1

    if new_full_solution.total_value > best_solution.total_value:
        # print "made better solution"
        best_solution = new_full_solution

    plot_ga_stats(ga_stats)

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
    crowd_size = 20
    population_size = 30
    generations = 30


    #
    # knapsack parameters
    #
    capacity = 50
    num_boxes = 10
    weight_max = 30
    value_max = 30


    boxes = create_boxes(num_boxes, weight_max, value_max)

    best_solution = wisdom_of_crowds(boxes, crowd_size, capacity, num_boxes, weight_max, population_size, generations)

    print "\nFINAL RESULT:", best_solution