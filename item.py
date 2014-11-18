
class Item():

    def __init__(self, id, weight, price, value):
        self.id = id
        self.weight = weight
        self.price = price
        self.value = value

    def __str__(self):
        return "ID: {0}\tWeight: {1}\tPrice: {2}\tValue: {3}".format(self.id, self.weight, self.price, self.value)

