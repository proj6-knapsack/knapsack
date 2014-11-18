
class Item():

    def __init__(self, id, weight, price, value, weight_max, price_max, value_max):
        self.id = id
        self.weight = weight
        self.price = price
        self.value = value
        self.weight_max = weight_max
        self.price_max = price_max
        self.value_max = value_max
        self.fitness = self.get_fitness()

    def __str__(self):
        return "ID: {0}\tValue: {1}\tPrice: {2}\tWeight: {3}\tFitness: {4}".format(self.id, self.value, self.price, self.weight, self.fitness)

    def get_fitness(self):
        # optimize  for high value, low price, low weight
        # have to normalize, then aggregate
        value_score = self.value/float(self.value_max)
        price_score = 1 - (self.price/float(self.price_max))
        weight_score = 1 - (self.weight/float(self.weight_max))
        return value_score + price_score + weight_score



