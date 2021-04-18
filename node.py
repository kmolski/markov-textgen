from collections import Counter
from random import choices


def frequencies(elems):
    length = len(elems)
    return {key: count / length for key, count in Counter(elems).items()}


class Node:
    def __init__(self, name, arrows):
        self.name = name
        self.arrows = arrows

    def __repr__(self):
        return self.name

    def walk(self, steps):
        node = self
        result = [self]
        for _ in range(steps, 0, -1):
            node = choices([x[0] for x in node.arrows], [x[1] for x in node.arrows])[0]
            result.append(node)
        return result


pizzas = Node("pizzas", [])
hamburgers = Node("hamburgers", [])
hot_dogs = Node("hot dogs", [])

pizzas.arrows = [(hot_dogs, 0.7), (hamburgers, 0.3)]
hamburgers.arrows = [(hamburgers, 0.2), (pizzas, 0.6), (hot_dogs, 0.2)]
hot_dogs.arrows = [(hot_dogs, 0.5), (hamburgers, 0.5)]

sample_of_10 = hamburgers.walk(10)
print("sample of 10: ", frequencies(sample_of_10))

sample_of_1000 = hamburgers.walk(1000)
print("sample of 1000: ", frequencies(sample_of_1000))

sample_of_1000000 = hamburgers.walk(1000000)
print("sample of 1000000: ", frequencies(sample_of_1000000))
