import os


def createFolder(path):
    if not os.path.exists(path):
        os.makedirs(path)
