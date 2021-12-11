alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def calculate_yx(yx: str):
    if yx[0] not in alphabet:
        return int(yx[0]), int(yx[1])

    return 8 - int(yx[1]), alphabet.index(yx[0])
