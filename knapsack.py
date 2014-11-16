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
import os
import csv
import time

DEBUG_EVOLUTION = False
DEBUG_WOC = True
SAVE_BOX_FILE = True # save this box configuration


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

    # data may contain empty values if no good solution was found during a generation.
    # replace those values with 0.
    for crowd_member in data:
        costs = []
        for x in crowd_member:
            if not x:
                costs.append(0)
            else:
                costs.append(x.total_value)
        p1 = plt.plot(ind, costs)
        color = random_color()
        p1[-1].set_color(color)

    plt.xlabel('Generations')
    plt.ylabel('Value')
    plt.grid(True)

    plt.xlim([0,N])

    plt.show()


def remove_items(solution, weight_max, boxes):
    # if total weight of child box config > capacity, remove boxes with low values
    if solution.total_weight > weight_max:
        boxes_sorted_by_value = sorted(boxes, key=lambda box: box.value, reverse=False)
        while boxes_sorted_by_value and solution.total_weight > weight_max:
            least_value_box = boxes_sorted_by_value.pop(0)
            if solution.box_stats[least_value_box.id] == 1:
                solution.box_stats[least_value_box.id] = 0
                solution.update_values()
    return solution



def mutate(box_collection, population):
    """
    :param box_collection:
    :return: mutated box_collection
    """
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
    num_to_switch = random.randint(0, len(box_collection.box_stats)-1)
    idx_to_switch = list()

    config_to_mutate = population.index(worst_box_config)

    while len(idx_to_switch) < num_to_switch:
        idx = random.randint(0, len(box_collection.box_stats)-1)
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

    # may be overweight, remove lowest value items
    x = remove_items(x, weight_max, boxes)

    if DEBUG_EVOLUTION:
        print "\tNEW VALUE:\t{0}".format(x)



def evolve_generation(population_size, capacity, boxes, num_boxes, weight_max, population=None):
    """
    :param population: list of box collections
    :return: list of evolved box collections
    """

    # if there is no starting population, build a random population
    if not population:
        population = list()
        for idx in range(population_size):
            boxes_outside = boxes[:]
            random.shuffle(boxes_outside)
            solution = defs.BoxCollection([0 for x in range(num_boxes)], 0, 0, boxes)
            while len(boxes_outside) > 0:
                chosen_box = boxes_outside.pop()
                if chosen_box.weight + solution.total_weight <= weight_max:
                    solution.box_stats[chosen_box.id] = 1
                    solution.update_values()

            population.append(solution)

    else:
        # there is a starting population, so:
        # 1. remove unfit adults
        # 2. copy the best adults as whole children
        # 3. fill out the population by crossing over adults into children

        # 1. remove any population members over the weight limit
        for s in population:
            if s.total_weight > weight_max:
                population.remove(s)

        # 2. build new population of best adults
        # sort population by value
        population = sorted(population, key=lambda solution: solution.total_value, reverse=True)
        parent_threshold = 0.4 # keep the best percentage of parents
        parent_threshold_count = int(population_size * parent_threshold)
        new_population = list()

        # 3. breed children until population is full
        while len(new_population) < population_size - parent_threshold_count:
            child = create_child(population, boxes, weight_max)
            new_population.append(child)

        # 4. mutate children if they're unlucky
        mutation_rate = 0.1
        num_to_mutate = int(math.ceil(population_size * mutation_rate))
        for i in range(num_to_mutate):
            random_item = random.choice(new_population)
            random_item = mutate(random_item, new_population)

        # add unmutated good parents to pool, to make sure we don't mess up our best solution
        new_population += population[:parent_threshold_count]

        # assign new generation to population
        population = new_population

    if DEBUG_EVOLUTION:
        for idx, solution in enumerate(population):
            print "\tPop Member {0}:\t{1}".format(idx, solution)

    return population



def create_child(population, boxes, weight_max):

    ######################################
    # crossover function
    #######################################

    parentA = random.choice(population)
    parentB = random.choice(population)

    # perform crossover:
    # child's first half is from best config, second half from second best config
    child = list()

    #divide configs into 2 parts
    length = int(math.ceil(len(boxes)/2))

    child = parentA.box_stats[0:length] + parentB.box_stats[length:num_boxes]

    # create boxCollection object
    child_box_config = defs.BoxCollection(child, 0, 0, boxes)
    child_box_config.update_values()

    # if total weight of child box config > capacity, remove boxes with low values
    child_box_config = remove_items(child_box_config, weight_max, boxes)

    return child_box_config



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

    # list of boxes contained inside a configuration?
    contents = list()

    # remember the best solutions from each generation.
    best_of_each_generation = list()

    start_time = time.time()

    ##################
    # GA parameters
    ##################

    population = None

    # evolve a solution through a number of generations
    for round_num in range(generations):

        if DEBUG_EVOLUTION:
            print "Evolution Generation #", round_num

        population = evolve_generation(population_size, capacity, boxes, num_boxes, weight_max, population)

        # END OF THIS GENERATION
        # find and record best population member from this generation
        optimal_collection = population[0]
        for x in population:
            if optimal_collection.total_weight > weight_max:
                optimal_collection = x
            elif (x.total_value >= optimal_collection.total_value) and (x.total_weight <= weight_max):
                optimal_collection = x
        best_of_each_generation.append(optimal_collection)
        if DEBUG_EVOLUTION:
            print "\tBEST:\t\t{0}".format(optimal_collection)


    # END OF ALL GENERATIONS
    # for idx, s in enumerate(best_of_each_generation):
    #     print "Best Sol. Gen. {0}:\t{1}".format(idx, s)
    # generation_best_values = [x.total_value for x in best_of_each_generation]

    elapsed_time = time.time() - start_time
    print "GA TIME:", elapsed_time

    return (optimal_collection, best_of_each_generation)





def wisdom_of_crowds(boxes, crowd_size, capacity, num_boxes, weight_max, population_size, generations):

    woc_start_time = time.time()
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
        if solution:
            if best_solution == None:
                best_solution = solution
            elif (solution.total_value > best_solution.total_value) and (solution.total_weight < weight_max):
                best_solution = solution


    # try to create even better solution by merging crowd's solutions
    # count which boxes are shared by the crowd
    shared_box_counts = [0 for x in range(num_boxes)]
    for idx, solution in enumerate(solutions):
        if solution:
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
        print "made better solution"
        best_solution = new_full_solution
    else:
        print "not better solution", new_full_solution


    elapsed_time = time.time() - woc_start_time
    print "WOC TIME:", elapsed_time

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

    # record boxes in text file
    if SAVE_BOX_FILE:
        filepath = os.path.split(os.path.realpath(__file__))[0]
        filename = "boxes.csv"
        full_filename = os.path.join(filepath, filename)
        with open(full_filename,'w') as f:
            a = csv.writer(f, delimiter=',')
            a.writerow(['ID', 'Value', 'Weight'])
            for box in boxes:
                a.writerow([box.id, box.value, box.weight])

    return boxes




if __name__ == "__main__":

    #
    # genetic algorithm and WoC parameters
    #
    crowd_size = 30
    population_size = 50
    generations = 50


    #
    # knapsack parameters
    #
    capacity = 1000
    num_boxes = 400
    weight_max = 50
    value_max = 50

    num_tests = 1
    for i in range(num_tests):
        boxes = create_boxes(num_boxes, weight_max, value_max)
        best_solution = wisdom_of_crowds(boxes, crowd_size, capacity, num_boxes, weight_max, population_size, generations)
        print "\nFINAL RESULT:", best_solution