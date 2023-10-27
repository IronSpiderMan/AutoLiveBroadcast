def read_to_list(filepath):
    with open(filepath, encoding='utf-8') as f:
        texts = f.readlines()
    return texts
