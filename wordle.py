"""
Wordle
Assignment 1
Semester 1, 2022
CSSE1001/CSSE7030
"""

from concurrent.futures import process
from string import ascii_lowercase
from typing import Optional

from support import (
    load_words,
    choose_word,
    VOCAB_FILE,
    ANSWERS_FILE,
    CORRECT,
    MISPLACED,
    INCORRECT,
    UNSEEN,
)

MAX_NUMBER_GUESSES = 6
LENGTH_WORDS = 6

__author__ = "Sylvia Lewis, s4326462"
__email__ = "sylvia.lewis@uqconnect.edu.au"

def has_won(guess: str, answer: str) -> bool:
    """ Returns True if the guess matches answer exactly. Otherwise, returns False.
    Precondition: len(guess) == 6 and len(answer) == 6

    Parameters:
        guess (str): The guess.
        answer (str): The word to guess.

    Returns:
        bool: True or False.

    """
    return (guess == answer)

def has_lost(guess_number: int) -> bool:
    """ Returns True if the number of guesses that have occurred, guess number, is equal to or greater
    than the maximum number of allowed guesses (in our case, six). Otherwise, returns False.

    Parameters:
        guess_number (int): The number of guesses that have occurred.

    Returns:
        bool: True or False.
    """
    return (guess_number >= MAX_NUMBER_GUESSES)

def remove_word(words: tuple[str, ...], word: str) -> tuple[str, ...]:
    """ Returns a copy of words with word removed, assuming that words contains word exactly once.

    Parameters:
        words (tuple<str,...>): The list of words.
        word (str): The word to be removed from words.

    Returns:
        tuple<str>: the list of words with word removed.
    """
    i = 0
    for w in words:
        if w == word:
            break
        i += 1
    return (words[:i] + words[i+1:])        #create a new tuple by merging two parts of the tuple "words" with the chosen element missing

def valid_guess(guess: str, words: tuple[str, ...]) -> bool:
    """ Checks whether a guess is a valid word.

    Parameters:
        guess (str): The guess.
        words (tuple<str,...>): The list of valid words.

    Returns:
        bool: True or False.

    """
    return (guess in words)

def prompt_user(guess_number: int, words: tuple[str, ...]) -> str:
    """ Prompts the user for the next guess, reprompting until either a valid guess
        is entered, or a selection for help, keyboard, or quit is made.

    Parameters:
        guess_number (int): the number of valid guesses already made.
        words (tuple<str>): List of valid words.

    Returns:
        str: The first valid guess or request for help, keyboard, or quit.
    """
    while (True):                #Continue prompting until valid input
        guess = input("Enter guess " + str(guess_number) + ": ")
        guess = guess.lower()
        if (len(guess) == 1 and (guess == "k" or guess == "q" or guess == "h" or guess == "a")):
            return (guess)          #valid input so return input
        if (len(guess) != 6):
            print("Invalid! Guess must be of length 6")
        if (len(guess) == 6):
            if (valid_guess(guess, words)):
                return (guess)          #valid input so return valid word
            print("Invalid! Unknown word")

def process_guess(guess: str, answer: str) -> str:
    """
    Returns a modified representation of guess, in which each letter is replaced by:
    - A green square if that letter occurs in the same position in answer;
    - A yellow square if that letter occurs in a different position in answer; or
    - A black square if that letter does not occur in answer.

    Precondition: len(guess) == 6 and len(answer) == 6
    """
    ret: list = list(INCORRECT * 6)
    for i in range(LENGTH_WORDS):
        next_occur = i                #for multiple instances of the same letter in the guess word
        pos = -1                    #position of the letter in the answer (if applicable)
        if guess[i] in answer:
            next_occur = guess[next_occur+1:].find(guess[i]) + i + 1
            pos = answer[pos + 1:].find(guess[i])
            if (pos == i):
                ret[i] = CORRECT
                answer = answer[0:i] + " " + answer[i+1:]        #remove letter so it isn't counted again if it appears in guess more than once
            elif (pos != next_occur):                    #if not(the letter appears more than once in guess word and is correctly placed the following instance)
                ret[i] = MISPLACED
                answer = answer[0: pos] + " " + answer[pos + 1:]
    return (''.join(ret))            #convert list of letters to string

def update_history(history: tuple[tuple[str, str], ...], guess: str, answer: str ) -> tuple[tuple[str, str], ...]:
    """ Returns a copy of history updated to include the latest guess and its processed form.

    Parameters:
        history (tuple<tuple<str,str>,...>):
        guess (str): the user's guess.
        answer (str): the answer.

    Returns:
        tuple<tuple<str,str>,...>: a copy of history updated to include the latest guess and it's processed form.
    """
    copy = {}
    copy = history + ((guess, process_guess(guess, answer)),)        #create a copy of history with new guess and processed guess appended
    return (copy)

def print_history(history: tuple[tuple[str, str], ...]) -> None:
    """
    Prints the guess history in a user-friendly way.

    Parameters:
        history (tuple<tuple<str, str>, ...>): The guess history

    Returns:
        None
    """
    i = 1
    for guess, answer in history:
        print(15 * "-")
        print("Guess " + str(i) + ": ", end=" ")
        for j in range(LENGTH_WORDS):
            if (j != LENGTH_WORDS - 1):
                print(guess[j], end=" ")
            else:
                print(guess[j], end='\n')
        print(9 * UNSEEN + answer, end="\n")
        i += 1
    print(15 * "-")
    print()
    return None

def print_keyboard(history: tuple[tuple[str, str], ...]) -> None:
    """
    Prints the keyboard in a user-friendly way with the information currently known about each letter.

    Parameters:
        history (tuple<tuple<str, str>, ...>): The guess history

    Returns:
        None
    """
    letters = ascii_lowercase
    infos = {letter : UNSEEN for letter in letters}
    for guess, answer in history:
        for letter in letters:
            for i in range(LENGTH_WORDS):
                if (letter == guess[i]):
                    if (infos[letter] != CORRECT and not (infos[letter] == MISPLACED and answer[i] == INCORRECT)):        #make sure CORRECTs aren't overwritten
                        infos[letter] = answer[i]
    print("\nKeyboard information")
    print(12 * "-")
    for key in infos:
        print(key + ": " + infos[key], end=('\n' if ord(key) % 2 == 0 else '\t'))
    print()
    return None

def print_stats(stats: tuple[int, ...]) -> None:
    """
    This function prints the stats in a user-friendly way.

    Parameters:
        stats (tuple<int, ...>): a tuple containing the number of games won in the acceptable number of moves, and the number of losses.

    Returns:
        None.
    """
    print("\nGames won in:")
    for i in range(MAX_NUMBER_GUESSES):
        print(i + 1, "moves:", stats[i])
    print("Games lost:", stats[6])
    return None

def was_guessed(word: str, history: tuple[tuple[str, str], ...]) -> bool:
    """
    Verifies the proposed word has already been guessed.

    Parameters:
        word (str): The proposed word.
        history (tuple<tuple<str, str>, ...>): The guess history

    Returns:
        False if the word hasn't been guessed before or True if it has.
    """
    for guess, answer in history:
        if (word == guess):
            return True
    return False

def count_letter_occurence(char: str, guess: str, answer: str) -> int:
    """
    Counts the number of times a letter appears in the word (correctly placed or misplaced).

    Parameters:
        char (str): The letter to count occurences for.
        guess (str): The guess word.
        answer (str): The answer word.
    
    Returns:
        The number of times the letter occurs.
    """
    ans = 0
    for i in range(LENGTH_WORDS):
        if (guess[i] == char):
            if (answer[i] == MISPLACED or answer[i] == CORRECT):
                ans += 1
    return ans

def guess_next(vocab: tuple[str, ...], history: tuple[tuple[str, str], ...]) -> Optional[str]:
    """
    Returns a valid next guess that doesn't violate known information from previous guesses.
    If no valid word remains in the vocabulary, this function returns None.

    Parameters:
        vocab (tuple<str, ...>): The potential words.
        history (tuple<tuple<str, str>, ...>): The history of guesses.

    Returns:
        A word as a proposed next guess if it finds one.
    """
    infos: dict[dict] = {}

    for c in ascii_lowercase:
        copy = c
        infos[c] = {
            "letter": copy,
            "minCount": 0,      #minimum number of times the letter appears in the word 
            "exactCount": -1,   #exact number of times the letter appears in the word (if known)
            "incorrectPos": [], #the positions where the letter cannot be placed
            "correctPos": []    #the position(s) where the letter must be placed
        }

    for guess, answer in history:
        for i in range(LENGTH_WORDS):
            letter = guess[i]
            #INCORRECT can either mean "none of this letter" or "no more occurences of this letter"
            #so let's figure out the exact number of occurences of the letter in the word
            if (infos[letter]["exactCount"] == -1 and answer[i] == INCORRECT):
                infos[letter]["exactCount"] = count_letter_occurence(guess[i], guess, answer)
                if (infos[letter]["exactCount"] == 0):   #if the letter isn't in the word then add letter to incorrectPos in all places
                    infos[letter]["incorrectPos"] = [x for x in range(LENGTH_WORDS)]
            else:   #we can work out the minumum number of times the letter appears
                minCount = count_letter_occurence(guess[i], guess, answer)
                if (minCount > infos[letter]["minCount"]):
                    infos[letter]["minCount"] = minCount
            if (answer[i] == MISPLACED):        #add position of misplaced letter to incorrectPos 
                infos[letter]["incorrectPos"] += [i]
            elif (answer[i] == CORRECT):        #add position of correctly placed letter to correctPos
                infos[letter]["correctPos"] += [i]

    possibilities = []
    for word in vocab:
        isValid = True
        if (was_guessed(word, history)):    #word already been guessed?
            continue                        #go directly to next word
        for key in infos:       #for each letter
            letterCountWord = word.count(infos[key]["letter"])     #count how many times the letter appears in the word
            if ((infos[key]["exactCount"] == -1 and letterCountWord >= infos[key]["minCount"])
                or (infos[key]["exactCount"] != -1 and letterCountWord == infos[key]["exactCount"])):   #doesn't contain letters that are incorrect or too many occurences of the letter
                for correctPos in infos[key]["correctPos"]:     #checking the correctly placed letters are correctly placed in next guess word
                    if (word[correctPos] != infos[key]["letter"]):  #if letter not in known correct position
                        isValid = False                             #word no longer valid
                        break                                       #stop investigating

                if (isValid == True):
                    letterIndex = -2
                    while (letterIndex != -1):
                        letterIndex = word.find(infos[key]["letter"], 0 if letterIndex == -2 else letterIndex + 1)
                        if (infos[key]["incorrectPos"].count(letterIndex)):     #if letter appears in an incorrect position
                            isValid = False                                     #word no longer valid
                            break                                               #stop investigating
            else:   #contains letter that is known incorrect or too many occurences of the letter 
                isValid = False

        if (isValid == True):       #validated our test?
            possibilities += [word] #add it to the list of possibile next guesses

    weighting = { "a": 8.2, "b": 1.5, "c": 2.7, "d": 4.7, "e": 13, "f": 2.2, "g": 2,
        "h": 6.2, "i": 6.9, "j": 0.16, "k": 0.81, "l": 4.0, "m": 2.7, "n": 6.7, "o": 7.8, 
        "p": 1.9, "q": 0.11, "r": 5.9, "s": 6.2, "t": 9.6, "u": 2.7, "v": 0.97, "w": 2.4,
        "x": 0.15, "y": 2, "z": 0.078 }         #weighting for each letter based on frequency (found on wikipedia: https://en.wikipedia.org/wiki/Letter_frequency)
                                                #could have calculated this based on the list of valid words
    resultWord: str = ""
    resultProb = -1
    for possibility in possibilities:
        prob = 0
        for letter in possibility:
            prob += weighting[letter]       #preference for words with common letters
            prob -= weighting[letter] / 2 * possibility.count(letter)   #but with variety, avoid guessing "entete" just because "e" and "t" are weighted highly

        if (prob > resultProb):     #word is weighted higher than the previous ones?
            resultProb = prob       #choose it as new best word
            resultWord = possibility

    print(resultWord)       #print the suggestion for the user
    return (resultWord)

def make_guess(guess_number: int, words: tuple[str, ...], history: tuple[tuple[str, str], ...]) -> Optional[str]:
    """
    Starts the round. Calls function to prompt user. Deals with single letter inputs.

    Parameters:
        guess_number (int): The number of valid guesses made.
        words (tuple<str, ...>): The list of valid words.
        history (tuple<tuple<str, str>, ...>): The history of guesses.

    Returns:
        The valid guess word or None if input is 'q' (eventually leading to the program quitting).
    """
    input = " "
    while (len(input) == 1):
        input = prompt_user(guess_number, words)
        input = input.lower()            #make sure it still works even with wEirD cApitAliSatiON and to avoid saying: input == 'q' or input == 'Q' etc
        if (len(input) == 1):
            if (input == 'q'):
                return None            #Stop everything! I quit!
            elif (input == 'h'):
                print("Ah, you need help? Unfortunate.")
            elif (input == 'a'):
                guess_next(words, history)
            elif (input == 'k'):
                print_keyboard(history)
    return (input)

def main():
    play: str = 'y'
    stats = (0, 0, 0, 0, 0, 0, 0)        #corresponds with: rounds won in (1 move, 2 moves, ... 6 moves, lost)
    words = load_words(VOCAB_FILE)
    answer_history = ()
    answer = ""
    while (play == 'y' or play == "Y"):
        answer = choose_word(load_words(ANSWERS_FILE))
        if answer in answer_history:
            while answer in answer_history:
                answer = choose_word(load_words(ANSWERS_FILE))
        answer_history = answer_history + (answer,)
        history = ()
        for guess_number in range(1, MAX_NUMBER_GUESSES + 1):
            guess = make_guess(guess_number, words, history)
            if (guess == None):        #user wants to quit
                return
            history = update_history(history, guess, answer)
            print_history(history)
            if (has_won(guess, answer)):
                break                    #no more moves when you've guessed correctly
        if (has_won(guess, answer)):
            stats = stats[:guess_number - 1] + (stats[guess_number - 1] + 1,) + stats[guess_number:]    #add win to stats
            print("Correct! You won in " + str(guess_number) + " guesses!")
        else:
            stats = stats[:-1] + (stats[- 1] + 1,)            #add loss to stats
            print("You lose! The answer was: " + answer)
        print_stats(stats)
        play = input("Would you like to play again (y/n)? ")

if __name__ == "__main__":
    main()
