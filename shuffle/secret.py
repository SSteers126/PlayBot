from secrets import randbelow as secretNumBelow

def secretShuffle(array, shuffles=None):
    if shuffles == None:
        shuffles = len(array)
    length = len(array)
    for shuffle in range(shuffles):
        for count, item in enumerate(array):

            idx = secretNumBelow(length)
            while idx == count:
                idx = secretNumBelow(length)

            # tmp = array[idx1]

            array[count] = array[idx]
            array[idx] = item

    return array

# Tests no cards have been copied
# print(sorted(secretShuffle(gen52Deck())) == sorted(gen52Deck()))
