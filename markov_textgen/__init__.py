"""A Markov chain-based text generation script."""
from collections.abc import Iterable
from itertools import chain, islice
from random import choice, choices
from typing import Optional, Tuple
import re

# Lists cannot be map keys, so the Prefix has to be a tuple
Prefix = Tuple[str, ...]
# Mapping from the word to its reference count
WordRef = dict[str, int]


class NoNodeFoundError(ValueError):
    def __init__(self, word: str):
        self.word = word


class Node:
    """The representation of a Markov chain node, which contains the word, and a list
    of arrows to other nodes, grouped by the prefixes of the word in the source text."""

    def __init__(self, word: str, arrows: dict[Prefix, WordRef]):
        self.word = word
        # Prefix to word reference count mapping
        self.arrows = arrows

    def __str__(self) -> str:
        return self.word

    def add_word(self, prefix: list[str], word: str) -> None:
        """Add the following word to the node. For example: given the text "a quick fox",
        the word 'quick' will be added to node 'a', and 'fox' to node 'quick'."""
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
    NON_WORD_PUNCTUATION_CHARS = re.compile(r"[^\w.?!]")

    def __init__(self, order: int):
        self.order = order
        # Word to chain Node mapping
        self.nodes: dict[str, Node] = {}

    def add_words(
        self,
        words: Iterable[str],
        normalise_case: bool = True,
        remove_non_word_chars: bool = True,
    ) -> None:
        """Add an iterable of words (strings) to the model. The words can be processed -
        they can be normalised to lowercase or have non-word characters removed."""

        def word_processor(word: str) -> str:
            result = word.strip()
            if normalise_case:
                result = result.lower()
            if remove_non_word_chars:
                result = self.NON_WORD_CHARS.sub("", result)
            return result

        words = (word_processor(w) for w in words)
        # `prefix` has to be a list here, since tuples don't support append() and pop()
        prefix = list(islice(words, self.order - 1))

        current_word = next(words)
        self.nodes[current_word] = Node(current_word, {})

        for next_word in words:
            self.nodes[current_word].add_word(prefix, next_word)
            # pop() comes after append() to avoid errors in Markov chains of order 1
            prefix.append(current_word)
            prefix.pop(0)
            current_word = next_word
            if current_word not in self.nodes:
                self.nodes[current_word] = Node(current_word, {})

    def walk(self, steps: int, init_word: Optional[str] = None) -> list[Node]:
        if init_word is None:
            node = choice(list(self.nodes.values()))
        else:
            try:
                node = self.nodes[init_word]
            except IndexError as e:
                raise NoNodeFoundError(init_word) from e

        init_vector = choice(list(node.arrows.keys()))
        # `prefix` has to be a list here, since tuples don't support append() and pop()
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

    def generate_string(self, max_words: int, sentences: bool = True) -> str:
        def is_capitalised(word: str) -> bool:
            return word[:1].isupper()

        def is_terminal(word: str) -> bool:
            filtered = self.NON_WORD_PUNCTUATION_CHARS.sub("", word)
            return bool(filtered) and filtered[-1] in ".?!"

        if sentences:
            # Start with a capitalised word
            init_words = [w for w in self.nodes.values() if is_capitalised(w.word)]
        else:
            init_words = list(self.nodes.values())

        start = choice(init_words)
        result = self.walk(max_words, start.word)

        if sentences and any(is_terminal(w.word) for w in result):
            # Remove words that don't end with punctuation
            while result and not is_terminal(result[-1].word):
                result.pop()

        return " ".join(w.word for w in result)


def model_from_str(
    string: str,
    order: int = 2,
    normalise_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from a string."""
    return model_from_words(
        string.split(),
        order=order,
        normalise_case=normalise_case,
        remove_non_word_chars=remove_non_word_chars,
    )


def model_from_file(
    filename: str,
    order: int = 2,
    normalise_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from an input file."""
    with open(filename, "r") as input_file:
        return model_from_lines(
            input_file,
            order=order,
            normalise_case=normalise_case,
            remove_non_word_chars=remove_non_word_chars,
        )


def model_from_lines(
    lines: Iterable[str],
    order: int = 2,
    normalise_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from an iterable of lines (strings)."""
    return model_from_words(
        chain.from_iterable(line.split() for line in lines),
        order=order,
        normalise_case=normalise_case,
        remove_non_word_chars=remove_non_word_chars,
    )


def model_from_words(
    words: Iterable[str],
    order: int = 2,
    normalise_case: bool = True,
    remove_non_word_chars: bool = True,
) -> Model:
    """Generate a Markov text model from an iterable of words (strings)."""
    model = Model(order)
    model.add_words(
        words,
        normalise_case=normalise_case,
        remove_non_word_chars=remove_non_word_chars,
    )
    return model
