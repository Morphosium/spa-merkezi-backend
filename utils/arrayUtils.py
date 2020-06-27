def containsInDictionaryKey(data : dict, keys : list) -> bool:
    flag = True
    incomingKeys = keys
    dataKeys = data.keys()
    for item in incomingKeys:
        flag = item in dataKeys
        if (flag is False):
            break
    return flag