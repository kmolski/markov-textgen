"""A Markov chain-based text generation script."""
from itertools import chain, islice
from random import choice, choices
import re


def model_from_str(string, order=2, normalize_case=True, remove_non_word_chars=True):
    """Generate a Markov text model from a string."""
    return model_from_words(
        string.split(),
        order=order,
        normalize_case=normalize_case,
        remove_non_word_chars=remove_non_word_chars,
    )


def model_from_file(filename, order=2, normalize_case=True, remove_non_word_chars=True):
    """Generate a Markov text model from an input file."""
    with open(filename, "r") as input_file:
        return model_from_lines(
            input_file,
            order=order,
            normalize_case=normalize_case,
            remove_non_word_chars=remove_non_word_chars,
        )


def model_from_lines(lines, order=2, normalize_case=True, remove_non_word_chars=True):
    """Generate a Markov text model from an iterable of lines (strings)."""
    return model_from_words(
        chain.from_iterable(l.split() for l in lines),
        order=order,
        normalize_case=normalize_case,
        remove_non_word_chars=remove_non_word_chars,
    )


def model_from_words(words, order=2, normalize_case=True, remove_non_word_chars=True):
    """Generate a Markov text model from an iterable of words (strings)."""
    model = Model(order)
    model.add_words(
        words,
        normalize_case=normalize_case,
        remove_non_word_chars=remove_non_word_chars,
    )
    return model


class Model:
    """The Markov chain representation that contains its nodes and provides
    methods for adding new words/randomly walking the structure."""

    __NON_WORD_CHARS = re.compile(r"\W")

    def __init__(self, order):
        self.order = order
        self.nodes = {}

    def add_words(self, words, normalize_case=True, remove_non_word_chars=True):
        def word_processor(word):
            result = word.strip()
            if normalize_case:
                result = result.lower()
            if remove_non_word_chars:
                result = self.__NON_WORD_CHARS.sub("", result)
            return result

        words = (word_processor(w) for w in words)
        prefix = list(islice(words, self.order - 1))
        current_word = next(words)

        for next_word in words:
            if current_word not in self.nodes:
                self.nodes[current_word] = Node(current_word, {})
            self.nodes[current_word].add_word(prefix, next_word)
            prefix.append(current_word)
            prefix.pop(0)
            current_word = next_word

    def walk(self, steps, init_word=None):
        if init_word is None:
            node = choice(list(self.nodes.values()))
        else:
            node = self.nodes[init_word]

        init_vector = list(choice(list(node.arrows.keys())))
        result = [node]

        for _ in range(steps):
            arrows = node.arrows[tuple(init_vector)]
            word = choices(list(arrows.keys()), arrows.values())[0]
            init_vector.append(node.name)
            init_vector.pop(0)
            node = self.nodes[word]
            result.append(node)

        return result


class Node:
    """The representation of a Markov chain node, which contains the 'name', or the
    word that the node represents, and a list of arrows to other nodes, grouped by
    the prefixes of the 'name' in the source text."""

    def __init__(self, name, arrows):
        self.name = name
        self.arrows = arrows

    def __repr__(self):
        return self.name

    def add_word(self, prefix, word):
        prefix = tuple(prefix)
        if prefix not in self.arrows:
            self.arrows[prefix] = {}
        if word not in self.arrows[prefix]:
            self.arrows[prefix][word] = 0
        self.arrows[prefix][word] += 1


jekyll_and_hyde_model = model_from_file(
    "dr_jekyll_and_mr_hyde.txt",
    order=3,
    normalize_case=False,
    remove_non_word_chars=False,
)
