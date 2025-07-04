import json
import random

from constants import hangman_stages, JSON_PATH


def print_secret_word_and_alphabet(
        stage: str,
        guess_word: list,
        alphabet: list) -> None:
    print(*alphabet)
    print(stage)
    print(*guess_word)


def start_play() -> None:
    alphabet = [
        'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
        'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
        'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'
    ]
    mistakes = 0
    guessed = 0
    with open(JSON_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)
        words = data["words"]
        secret_word = random.choice(words).upper()
        guessed_word = ['_'] * len(secret_word)
    while ((len(hangman_stages) - 1) != mistakes and
           len(secret_word) != guessed):
        print_secret_word_and_alphabet(
            hangman_stages[mistakes], guessed_word, alphabet)
        letter = input("Введите одну букву: ")
        letter = letter.upper()
        if letter not in alphabet:
            print(
                'Вы уже выбирали эту букву или это буква на английском, '
                'введите букву на русском'
            )
            continue
        if letter in secret_word:
            for i in range(len(secret_word)):
                if letter == secret_word[i]:
                    guessed += 1
                    guessed_word[i] = letter
        else:
            mistakes += 1
        letter_index = alphabet.index(letter)
        alphabet[letter_index] = '_'
    if len(secret_word) == guessed:
        print("Поздравляем, вы победили!")
    else:
        print("К сожалению вы проиграли :(")
    main()


def main() -> None:
    print("Приветствуем в игре виселица. Выберите один из вариантов:")
    print("1) Начать новую игру\n2) Выйти")
    choice = 0
    while (choice != 1 and choice != 2):
        choice = input()
        try:
            choice = int(choice)
            if choice == 1:
                start_play()
            if choice == 2:
                break
        except:
            print("Вы ввели неверные данные, введите 1 или 2")


if __name__ == "__main__":
    main()
