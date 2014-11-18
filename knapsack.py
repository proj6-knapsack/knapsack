############################################################################
## Knapsack Problem:
## Given a number of objects n with weights w and value v,
## how can they be placed in a knapsack with capacity c
## as to maximize the total value within?
############################################################################


import os
import csv
import time
import math

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from utils import *
from item import Item
from itemcollection import ItemCollection


DEBUG_EVOLUTION = True
DEBUG_WOC = True
SAVE_FILE = True # save this item configuration



###################
# WISDOM OF CROWDS
###################

def wisdom_of_crowds(items, crowd_size, capacity, num_items, population_size, generations):

    woc_start_time = time.time()
    solutions = []
    best_solution = None
    ga_stats = [] # list of stats for each crowd member's evolution

    for c in range(crowd_size):
        print "\nCROWD #", c
        solution_tuple = genetic_algorithm(items, capacity, num_items, population_size, generations)
        solution = solution_tuple[0]
        solutions.append(solution)
        ga_stats.append(solution_tuple[1])

        if DEBUG_WOC:
            print "CROWD SOLUTION", c, ":", solution
        if solution:
            if best_solution == None:
                best_solution = solution
            elif (solution.total_value > best_solution.total_value) and (solution.total_weight < capacity):
                best_solution = solution

    # try to create even better solution by merging crowd's solutions
    # count which items are shared by the crowd
    shared_item_counts = [0 for x in range(num_items)]
    for idx, solution in enumerate(solutions):
        if solution:
            for idx in range(num_items):
                if solution.item_stats[idx] == 1:
                    shared_item_counts[idx] += 1

    # create a new solution from items which are shared by the majority of the solutions
    threshold = 0.5 # percentage of crowd that must share this item for it to be considered for the new solution
    threshold_count = int(crowd_size * threshold)
    new_solution = [0 for x in range(num_items)]
    for idx, item in enumerate(shared_item_counts):
        if item >= threshold_count:
            new_solution[idx] = 1

    new_full_solution = ItemCollection(new_solution, items)

    # if the item is over weight, remove objects until within weight
    new_full_solution.limit_weight(weight_max)

    # try to find any other items we can add while remaining within the weight limit
    # sort them by value so we will use the higher-value items first
    found = False
    idx = 0
    items_sorted_by_value = sorted(items, key=lambda item: item.fitness, reverse=True)
    while not found and idx < num_items:
        if new_full_solution.item_stats[idx] == 0:
            highest_value_item = items_sorted_by_value.pop(0)
            new_weight = new_full_solution.total_weight + highest_value_item.weight
            if new_weight <= capacity:
                new_full_solution.item_stats[idx] = 1
                new_full_solution.update_values()
                found = True
        idx += 1

    if new_full_solution.total_fitness > best_solution.total_fitness:
        print "made better solution"
        best_solution = new_full_solution
    else:
        print "not better solution", new_full_solution

    elapsed_time = time.time() - woc_start_time
    print "WOC TIME:", elapsed_time

    plot_ga_stats(ga_stats)

    return best_solution



###################
# GENETIC ALGORITHM
###################

def genetic_algorithm(items, capacity, num_items, population_size, generations):
    """
    :return: tuple
    0: itemCollection instance with optimal packing (greatest value and lowest weight)
    1: list of values for the best solution from each generation - used in stats
    """
    start_time = time.time()  # record the runtime for the GA

    # track best solutions
    best_of_each_generation = list() # list of best solutions, one for each generation
    optimal_collection = None # single best solution from all generations
    population = None # stores evolving population, starts with nothing

    # evolve a solution for a number of generations
    for round_num in range(generations):
        if DEBUG_EVOLUTION:
            print "Evolution Generation #", round_num

        population = evolve_generation(population_size, capacity, items, num_items, population)

        # find and record best population member from this generation
        optimal_collection = population[0]
        for x in population:
            if optimal_collection.total_weight > capacity:
                optimal_collection = x
            elif (x.total_fitness >= optimal_collection.total_fitness) and (x.total_weight <= capacity):
                optimal_collection = x
        best_of_each_generation.append(optimal_collection)
        if DEBUG_EVOLUTION:
            print "\tBEST:\t\t{0}".format(optimal_collection)

    elapsed_time = time.time() - start_time
    print "GA TIME:", elapsed_time

    return (optimal_collection, best_of_each_generation)


def evolve_generation(population_size, capacity, items, num_items, population=None):
    """
    Optimizing for high value, low price, within capacity.
    :param population: list of item collections
    :return: list of evolved item collections
    """

    # if there is no starting population, build a random population
    if not population:
        population = list()
        for idx in range(population_size):
            items_stack = items[:]
            random.shuffle(items_stack)
            solution = ItemCollection([0 for x in range(num_items)], items) # empty solution
            while len(items_stack) > 0:
                chosen_item = items_stack.pop()
                if (chosen_item.weight + solution.total_weight) <= capacity:
                    solution.item_stats[chosen_item.id] = 1
                    solution.update_values()
            population.append(solution)

    else:
        # there is a starting population so...
        # 1. remove any population members over the weight limit
        for s in population:
            if s.total_weight > capacity:
                population.remove(s)

        # 2. save best adults for un-mutated reproduction later
        population = sorted(population, key=lambda solution: solution.total_fitness, reverse=True)
        parent_threshold_count = int(population_size * parent_threshold)
        best_parents = population[:parent_threshold_count]

        # 3. breed children until population is full
        new_population = list()
        while len(new_population) < population_size - parent_threshold_count: # save room to add best parents later
            child = create_child(population, capacity)
            new_population.append(child)

        # 4. mutate children if they're unlucky
        num_to_mutate = int(math.ceil(population_size * mutation_rate))
        for i in range(num_to_mutate):
            mutate( random.choice(new_population) )

        # add un-mutated good parents to pool, to make sure we don't mess up our best solution
        new_population += best_parents

        # assign new generation to population
        population = new_population

    if DEBUG_EVOLUTION:
        for idx, solution in enumerate(population):
            print "\tPop Member {0}:\t{1}".format(idx, solution)

    return population


def create_child(population, capacity):
    """
    Choose 2 random parents and cross-over their chromosomes
    :param population: list of ItemCollections (solutions)
    :param capacity: max allowable weight for child
    :return: ItemCollection child
    """
    parentA = random.choice(population)
    parentB = random.choice(population)
    items = parentA.items

    # perform crossover:
    # child's first half is from best config, second half from second best config

    length = int(math.ceil(len(items)/2))

    child = parentA.item_stats[0:length] + parentB.item_stats[length:num_items]

    # create itemCollection object
    child_item_config = ItemCollection(child, items)

    # if total weight of child item config > capacity, remove items with low values
    child_item_config.limit_weight(capacity)

    return child_item_config


def mutate(item_collection):
    """
    Perform mutation on item_collection object within population
    :param item_collection:
    :return: None
    """

    # mutate random number of indices
    num_to_switch = random.randint(0, len(item_collection.item_stats)-1)
    idx_to_switch = [random.randint(0, len(item_collection.item_stats)-1) for x in range(num_to_switch)]

    for y in idx_to_switch:
        if item_collection.item_stats[y] == 0:
            item_collection.item_stats[y] = 1
        else:
            item_collection.item_stats[y] = 0

    # have to recompute value and cost for mutated element
    item_collection.update_values()

    # may be overweight, remove lowest value items
    item_collection.limit_weight(capacity)

    if DEBUG_EVOLUTION:
        print "\tNEW VALUE:\t{0}".format(item_collection)

    return item_collection


def plot_ga_stats(data):
    """
    Display a line graph of the performance of the crowd's evolution.
    :param data: A list that includes each crowd member's performance.
                Each list entry is a list of that crowd member's
                best solution's value over all generations.
    """
    N = len(data[0])
    ind = xrange(N)
    # data may contain empty values if no good solution was found during a generation.
    # replace those values with 0.
    for crowd_member in data:
        costs = []
        for x in crowd_member:
            if not x:
                costs.append(0)
            else:
                costs.append(x.total_fitness)
        p1 = plt.plot(ind, costs)
        color = random_color()
        p1[-1].set_color(color)
    plt.xlabel('Generations')
    plt.ylabel('Value + (1-Price) + (1-Weight)')
    plt.grid(True)
    plt.xlim([0,N])
    plt.show()


def create_items(num_items, weight_max, value_max, price_max):
    """
    Create a collection of n random objects with weights w, values v, prices p
    :param num_items: int
    :param weight_max: int
    :param value_max: int
    :param price_max: int
    :return: list of Item objects
    """
    items = list()
    for i in range(num_items):
        weight = random.randint(1, weight_max)
        value = random.randint(1, value_max)
        price = random.randint(1, price_max)
        item = Item(i, weight, value, price, weight_max, value_max, price_max)
        items.append(item)
    if SAVE_FILE:
        save_items(items)
    return items


def save_items(items):
    """
    Save CSV file of the Items.
    :param items: list of Items
    """
    filepath = os.path.split(os.path.realpath(__file__))[0]
    filename = "items.csv"
    full_filename = os.path.join(filepath, filename)
    with open(full_filename,'w') as f:
        a = csv.writer(f, delimiter=',')
        a.writerow(['ID', 'Value', 'Price', 'Weight'])
        for item in items:
            a.writerow([item.id, item.value, item.price, item.weight])


if __name__ == "__main__":

    # genetic algorithm and WoC parameters
    crowd_size = 20
    population_size = 50
    generations = 30
    mutation_rate = 0.2
    parent_threshold = 0.2  # the best percentage of parents to keep

    # knapsack parameters
    capacity = 200
    num_items = 20
    weight_max = 50
    value_max = 50
    price_max = 100

    # run multiple tests if so desired
    num_tests = 1
    for i in range(num_tests):
        #create items with randomized weights and values
        items = create_items(num_items, weight_max, value_max, price_max)
        #crowd-source the best solutions based on the results from a genetic algorithm
        best_solution = wisdom_of_crowds(items, crowd_size, capacity, num_items, population_size, generations)
        print "\nFINAL RESULT:", best_solution