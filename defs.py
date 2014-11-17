
# data for each individual box:
# id, weight, value, and bool value for whether it's inside or outside the knapsack
class Box():

    def __init__(self, id, weight, value, inside=False):
        self.id = id
        self.weight = weight
        self.value = value
        self.inside = inside

    def __str__(self):
        return "ID: {0}\tWeight: {1}\tValue: {2}".format(self.id, self.weight, self.value)


# data for each box configuration:
# bool values for each box within the knapsack, total weight, total value, and data about each box within
class BoxCollection():

    def __init__(self, box_stats, total_weight, total_value, boxes):
        self.box_stats = box_stats
        self.total_weight = total_weight
        self.total_value = total_value
        self.boxes = boxes

    # update configuration stats upon mutation/crossover
    def update_values(self):
        self.total_value = 0
        self.total_weight = 0
        for index, value in enumerate(self.box_stats):
            if value == 1:
                self.total_value += self.boxes[index].value
                self.total_weight += self.boxes[index].weight

    def __str__(self):
        return "{0}\tValue: {1}\tCost: {2}".format(self.box_stats, self.total_value, self.total_weight)


# find configuration with maximized value
def find_best_config(population):

    best_config = None
    max_value = None

    for x in population:
        if x.total_value > max_value:
            max_value = x.total_value
            best_config = x

    return best_config