def chunked(list: list, size):
    """Chunks a list into inputted size lists"""
    for i in range(0, len(list), size):
        yield list[i:i + size]