def containsInDictionaryKey(dictionary : dict, keys : list) -> bool:
    flag = True
    incomingKeys =  dictionary.keys()
    for item in incomingKeys:
        flag = item in keys
        if (flag is False):
            break
    return flag