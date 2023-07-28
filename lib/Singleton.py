# Autor: Andrii Shapovalov
# Company: eGA
# Date: 2023-07-19
# Description: Singleton decorator

def singleton(class_):
    """Singleton decorator"""
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
