
class ItemCollection():

    def __init__(self, item_stats, items):
        self.item_stats = item_stats
        self.items = items
        self.total_weight = 0
        self.total_price = 0
        self.total_value = 0
        self.update_values()

    def update_values(self):
        """
        Calculate total weight, cost and value for collection
        and store result in this object's properties.
        """
        for index, value in enumerate(self.item_stats):
            if value == 1:
                self.total_weight += self.items[index].weight
                self.total_price += self.items[index].price
                self.total_value += self.items[index].value


    def limit_weight(self, weight_max):
        """
        Test a solution for being within the weight limit. If it's overweight,
        remove items until it's fixed then return the corrected solution.
        :param weight_max: int
        """
        # remove items with low values
        if self.total_weight > weight_max:
            items_sorted_by_value = sorted(self.items, key=lambda item: item.value, reverse=False)
            while items_sorted_by_value and self.total_weight > weight_max:
                least_value_item = items_sorted_by_value.pop(0)
                if self.item_stats[least_value_item.id] == 1:
                    self.item_stats[least_value_item.id] = 0
                    self.update_values()


    def __str__(self):
        return "{0}\tValue: {1}\tCost: {2}\tWeight: {3}".format(self.item_stats, self.total_value, self.total_price, self.total_weight)
