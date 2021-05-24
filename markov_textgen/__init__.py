"""A Markov chain-based text generation script."""
from collections.abc import Iterable
from itertools import chain, islice
from random import choice, choices
from typing import Optional, Tuple
import re

Prefix = Tuple[str, ...]
WordRef = dict[str, int]


class Node:
    """The representation of a Markov chain node, which contains the word, and a list
    of arrows to other nodes, grouped by the prefixes of the word in the source text."""

    def __init__(self, word: str, arrows: dict[Prefix, WordRef]):
        self.word = word
        self.arrows = arrows

    def __repr__(self) -> str:
        return self.word

    def add_word(self, prefix: list[str], word: str) -> None:
        prefix = tuple(prefix)
        if prefix not in self.arrows:
            self.arrows[prefix] = {}
        if word not in self.arrows[prefix]:
            self.arrows[prefix][word] = 0
        self.arrows[prefix][word] += 1


class Model:
    """The Markov chain representation that contains its nodes and provides
    methods for adding new words/randomly walking the structure."""

    NON_WORD_CHARS = re.compile(r"\W")

    def __init__(self, order: int):
        self.order = order
        self.nodes: dict[str, Node] = {}

    def add_words(
        self,
        words: Iterable[str],
        normalize_case: bool = True,
        remove_non_word_chars: bool = True,
    ) -> None:
        """Add words to the model."""

        def word_processor(word: str) -> str:
            result = word.strip()
            if normalize_case:
                result = result.lower()
            if remove_non_word_chars:
                result = self.NON_WORD_CHARS.sub("", result)
            return result

        words = (word_processor(w) for w in words)
        prefix = list(islice(words, self.order - 1))

        current_word = next(words)
        self.nodes[current_word] = Node(current_word, {})

        for next_word in words:
            self.nodes[current_word].add_word(prefix, next_word)
            prefix.append(current_word)
            prefix.pop(0)
            current_word = next_word
            if current_word not in self.nodes:
                self.nodes[current_word] = Node(current_word, {})

    def walk(self, steps: int, init_word: Optional[str] = None) -> list[Node]:
        if init_word is None:
            node = choice(list(self.nodes.values()))
        else:
            node = self.nodes[init_word]

        init_vector = choice(list(node.arrows.keys()))
        prefix = list(init_vector)
        result = [node]

        for _ in range(steps):
            arrows = node.arrows[tuple(prefix)]
            word = choices(list(arrows.keys()), list(arrows.values()))[0]
            prefix.append(node.word)
            prefix.pop(0)
            node = self.nodes[word]
            result.append(node)

        return result


def model_from_str(
    string: str,
    order: int = 2,
    normalize_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from a string."""
    return model_from_words(
        string.split(),
        order=order,
        normalize_case=normalize_case,
        remove_non_word_chars=remove_non_word_chars,
    )


def model_from_file(
    filename: str,
    order: int = 2,
    normalize_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from an input file."""
    with open(filename, "r") as input_file:
        return model_from_lines(
            input_file,
            order=order,
            normalize_case=normalize_case,
            remove_non_word_chars=remove_non_word_chars,
        )


def model_from_lines(
    lines: Iterable[str],
    order: int = 2,
    normalize_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from an iterable of lines (strings)."""
    return model_from_words(
        chain.from_iterable(line.split() for line in lines),
        order=order,
        normalize_case=normalize_case,
        remove_non_word_chars=remove_non_word_chars,
    )


def model_from_words(
    words: Iterable[str],
    order: int = 2,
    normalize_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from an iterable of words (strings)."""
    model = Model(order)
    model.add_words(
        words,
        normalize_case=normalize_case,
        remove_non_word_chars=remove_non_word_chars,
    )
    return model


jekyll_and_hyde_model = model_from_file(
    "dr_jekyll_and_mr_hyde.txt",
    order=3,
    normalize_case=False,
    remove_non_word_chars=False,
)
