from collections import Counter
from random import choices
import re


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


with open("dr_jekyll_and_mr_hyde.txt", "r") as input_file:
    text = input_file.read()

non_word_chars = re.compile(r"\W")
words = [word.lower() for word in text.split()]

current_word = words[0]
graph = {words[0]: {}}

for next_word in words[1:]:
    if next_word not in graph[current_word]:
        graph[current_word][next_word] = 0
    graph[current_word][next_word] += 1
    current_word = next_word
    if current_word not in graph:
        graph[current_word] = {}

nodes = {}
for word in graph:
    nodes[word] = Node(word, [])

for word, arrows in graph.items():
    total_edges = sum(edge_count for edge_count in arrows.values())
    nodes[word].arrows = [
        (nodes[w], count / total_edges) for w, count in arrows.items()
    ]


def frequencies(elems):
    length = len(elems)
    return {key: count / length for key, count in Counter(elems).items()}


print(" ".join(n.name for n in nodes["i"].walk(20)))
