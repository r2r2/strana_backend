

def get_difference_between_two_dicts(dict_1: dict, dict_2: dict) -> dict:
    """
    Возвращает новый словарь, который содержит разницу между словарями.

    :param dict_1: первый словарь
    :param dict_2: второй словарь
    :return: словарь, содержащий разницу между словарями
    """
    difference: dict = dict()
    # Ищем ключи, которые есть только в первом словаре
    for key in dict_1.keys():
        if key not in dict_2:
            difference[key] = dict_1[key]

    # Ищем ключи, которые есть только во втором словаре
    for key in dict_2.keys():
        if key not in dict_1:
            difference[key] = dict_2[key]

    # Ищем ключи, которые есть в обоих словарях, но с разными значениями
    for key in dict_1.keys() & dict_2.keys():
        if dict_1[key] != dict_2[key]:
            difference[key] = dict_1[key], dict_2[key]
    return difference
