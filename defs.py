
class Box():

    def __init__(self, id, weight, value, inside=False):
        self.id = id
        self.weight = weight
        self.value = value
        self.inside = inside

class BoxCollection():

    def __init__(self, box_stats, total_weight, total_value, boxes):
        self.box_stats = box_stats
        self.total_weight = total_weight
        self.total_value = total_value
        self.boxes = boxes

    def update_values(self):
        self.total_value = 0
        self.total_weight = 0
        for index, value in enumerate(self.box_stats):
            if value == 1:
                self.total_value += self.boxes[index].value
                self.total_weight += self.boxes[index].weight


#currently crossover algorithm just swaps the first half of the fittest configuration w/that of the second fittest
def crossover(population):
    print "crossover"