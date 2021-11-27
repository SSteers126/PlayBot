from secrets import randbelow

def coinFlip():
    choice = randbelow(2)
    print(choice)
    if choice == 1:
        return "Tails"
    else:
        return "Heads"