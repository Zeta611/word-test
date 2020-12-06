import random
import re
from typing import Dict
import warnings


class WordData:
    """Contains a meaning and a priority, which defaults to 0."""

    def __init__(self, meaning: str, priority: int = 0) -> None:
        self.meaning = meaning
        self.priority = priority

    def __repr__(self) -> str:
        return (
            f"WordData(meaning: '{self.meaning}', priority: {self.priority})"
        )

    def __str__(self) -> str:
        return f"'{self.meaning}': {self.priority}"


def read_words(filename: str = "words.txt") -> Dict[str, WordData]:
    """Returns a dictionary of words to `WordData`s read from `filename`."""

    # `line` is should be of format: `<word>:<meaning>[::<priority>]`
    format = re.compile(r"([^:]+):(.*(?=::)|.*)(?:::)?(\d+)?")
    word_meanings = {}
    with open(filename, "r", encoding="utf-8") as file:
        for number, line in enumerate(file):
            line = line.strip()
            # Skip blank lines
            if not line:
                continue

            result = format.match(line)
            if result:
                word, meaning, priority = result.groups()
                word = word.strip()
                meaning = meaning.strip()
                word_meanings[word] = WordData(
                    meaning, -1 if priority is None else int(priority)
                )
            else:
                warnings.warn(
                    f"File '{filename}', line {number}\n: {line}\n"
                    "  Correct format: `<word>:<meaning>[::<priority>]`",
                    SyntaxWarning,
                )
    return word_meanings


def write_words(
    word_meanings: Dict[str, WordData], filename: str = "words.txt"
) -> None:
    """Writes the contents of `words` to `filename`."""

    with open(filename, "w", encoding="utf-8") as file:
        for word in word_meanings:
            data = word_meanings[word]
            file.write(f"{word}:{data.meaning}::{data.priority}\n")


def normalize_priority(priority: int, max_priority: int) -> float:
    if priority < 0:
        return abs(max_priority) + 1
    if priority == 0:
        return 0.1
    return priority


def sample_words(
    word_meanings: Dict[str, WordData], size: int = 20
) -> Dict[str, WordData]:
    words = list(word_meanings.keys())
    priorities = [data.priority for data in word_meanings.values()]
    normalized_priorities = list(
        map(lambda p: normalize_priority(p, max(priorities)), priorities)
    )
    chosen_words = random.choices(words, weights=normalized_priorities, k=size)
    return {word: word_meanings[word] for word in chosen_words}


# def test_words()


warnings.simplefilter("default")
info = read_words()
# write_words(info)
print(sample_words(info))
