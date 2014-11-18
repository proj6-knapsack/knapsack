
class ItemCollection():

    def __init__(self, item_stats, items):
        self.item_stats = item_stats
        self.items = items
        self.total_weight = 0
        self.total_price = 0
        self.total_value = 0
        self.total_fitness = 0
        self.update_values()


    def update_values(self):
        """
        Calculate total weight, cost and value for collection
        and store result in this object's properties.
        """
        # have to reset params to 0 when recalculating
        self.total_weight = self.total_price = self.total_value = self.total_fitness = 0
        for index, value in enumerate(self.item_stats):
            if value == 1:
                self.total_weight += self.items[index].weight
                self.total_price += self.items[index].price
                self.total_value += self.items[index].value
                self.total_fitness += self.items[index].fitness


    def limit_weight(self, weight_max):
        """
        Test a solution for being within the weight limit. If it's overweight,
        remove items until it's fixed then return the corrected solution.
        :param weight_max: int
        """
        # remove items with low values
        if self.total_weight > weight_max:
            items_sorted_by_fitness = sorted(self.items, key=lambda item: item.fitness, reverse=False)
            while items_sorted_by_fitness and self.total_weight > weight_max:
                least_fit_item = items_sorted_by_fitness.pop(0)
                if self.item_stats[least_fit_item.id] == 1:
                    self.item_stats[least_fit_item.id] = 0
                    self.update_values()  # have to update each time an item is change to recompute weight


    def __str__(self):
        return "{0}\tValue: {1}\tPrice: {2}\tWeight: {3}\tFitness: {4}".format(self.item_stats, self.total_value, self.total_price, self.total_weight, self.total_fitness)
