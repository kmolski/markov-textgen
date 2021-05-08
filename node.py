from collections import Counter
from itertools import chain, islice
from random import choice, choices
import re


def model_from_str(string, **options):
    return model_from_lines(string.splitlines(), **options)


def model_from_file(file_name, **options):
    with open(file_name, "r") as input_file:
        return model_from_lines(input_file, **options)


def model_from_lines(lines, order=2, **format_options):
    model = Model(order)
    model.add_phrases_from_lines(lines, **format_options)
    return model


class Model:
    __NON_WORD_CHARS = re.compile(r"\W")

    def __init__(self, order):
        self.order = order
        self.nodes = {}

    def add_phrase_from_words(
        self, words, normalize_case=True, remove_non_word_chars=True
    ):
        def word_processor(s):
            result = s.strip()
            if normalize_case:
                result = result.lower()
            if remove_non_word_chars:
                result = self.__NON_WORD_CHARS.sub("", result)
            return result

        it = (word_processor(w) for w in words)
        prefix = list(islice(it, self.order - 1))
        current_word = next(it)

        for next_word in it:
            if current_word not in self.nodes:
                self.nodes[current_word] = Node(current_word, {})
            self.nodes[current_word].add_word(tuple(prefix), next_word)
            prefix.append(current_word)
            prefix.pop(0)
            current_word = next_word

    def add_phrases_from_lines(
        self, lines, phrase_per_line=False, **word_processor_options
    ):
        if phrase_per_line:
            for line in lines:
                self.add_phrase_from_words(line.split(), **word_processor_options)
        else:
            self.add_phrase_from_words(
                chain.from_iterable(l.split() for l in lines), **word_processor_options
            )

    def walk(self, steps, init_word=None):
        if init_word is None:
            node = choice(list(self.nodes.values()))
        else:
            node = self.nodes[init_word]

        init_vector = list(choice(list(node.arrows.keys())))
        result = [node]

        for _ in range(steps):
            arrows = node.arrows[tuple(init_vector)]
            word = choices([x for x in arrows.keys()], [x for x in arrows.values()])[0]
            init_vector.append(node.name)
            init_vector.pop(0)
            node = self.nodes[word]
            result.append(node)

        return result


class Node:
    def __init__(self, name, arrows):
        self.name = name
        self.arrows = arrows
        self.ref_count = 0

    def __repr__(self):
        return self.name

    def add_word(self, prefix, word):
        self.ref_count += 1
        if prefix not in self.arrows:
            self.arrows[prefix] = {}
        if word not in self.arrows[prefix]:
            self.arrows[prefix][word] = 0
        self.arrows[prefix][word] += 1


model = model_from_file("dr_jekyll_and_mr_hyde.txt", order=3)
