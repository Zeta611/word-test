from nptyping import NDArray
import numpy as np
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


def normalize_weights(weights: NDArray) -> None:
    """Convert non-positive weights, and normalize weights to sum to 1."""

    max_w = max(weights)
    if max_w < 0:
        max_w = 0

    for i, w in enumerate(weights):
        if w < 0:
            weights[i] = max_w + 1
        elif w == 0:
            weights[i] = 0.1
    weights /= sum(weights)


def sample_words(
    word_meanings: Dict[str, WordData], size: int = 20
) -> Dict[str, WordData]:
    words = list(word_meanings.keys())
    priorities = np.fromiter(
        (data.priority for data in word_meanings.values()), float
    )
    normalize_weights(priorities)
    chosen_words = np.random.choice(words, size, replace=False, p=priorities)
    return {word: word_meanings[word] for word in chosen_words}


def prompt(text: str = "", default: bool = True) -> bool:
    option_prompt = f"[{'Y' if default else 'y'}/{'n' if default else 'N'}]"
    while True:
        response = input(f"{text} {option_prompt}\n").lower()
        if response == "":
            return default
        elif response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False


def test_words(filename: str = "words.txt", size: int = 20) -> None:
    answer_cnt = 0
    wrong_words = []

    meanings = read_words(filename)
    chosen_words = sample_words(meanings, size)

    for i, word in enumerate(chosen_words):
        input(f"{i + 1}. What is the meaning of '{word}'?")
        correct = prompt(
            f"The meaning for {word} is {chosen_words[word].meaning}. Did you get it right?"
        )
        print()

        if correct:
            answer_cnt += 1
        else:
            wrong_words.append(word)

        if chosen_words[word].priority <= 0:
            meanings[word].priority = 0 if correct else 1
        else:
            meanings[word].priority -= 1 if correct else -1

    percentage = answer_cnt / size * 100
    print(f"You got {answer_cnt} out of {size} words. That is {percentage}%.")

    print("You need to practice more with following words:")
    for word in wrong_words:
        print(f"{word}: {chosen_words[word].meaning}")
    print()

    if prompt("Save progress?"):
        write_words(meanings, filename)
        print("Saved!")
    else:
        print("Current round discarded.")


warnings.simplefilter("default")
test_words("words.txt", size=20)
