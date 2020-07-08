def pagination(array, page, size):
    if page is not None and size is not None:
        if type(page) is str and page.isnumeric():
            page = int(page)
        if type(size) is str and size.isnumeric():
            size = int(size)

        p = page - 1
        start = p * size
        end = page * size
        return array[start:end]
    else:
        return array