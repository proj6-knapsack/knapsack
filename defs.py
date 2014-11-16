
class Box():

    def __init__(self, id, weight, value, inside=False):
        self.id = id
        self.weight = weight
        self.value = value
        self.inside = inside

class BoxCollection():

    def __init__(self, box_stats, total_weight, total_value):
        self.box_stats = box_stats
        self.total_weight = total_weight
        self.total_value = total_value