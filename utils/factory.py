from pattern.composite import *

def createItem(isFolder, data):
    (name, size, content, path, createAt, updateAt) = data

    if isFolder:
        return CFolder(name, path, createAt, updateAt)
    else:
        return CFile(name, path, content, size, createAt, updateAt)
