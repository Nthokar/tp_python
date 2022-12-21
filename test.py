from multiprocessing import Process, Queue

def f(q):
    q.put([42, None, 'hello'])

def b(dict1, dict2):
    for key2 in dict2:
        if dict1.keys().__contains__(key2):
            dict1[key2] += dict2[key2]
        else:
            dict1.update({key2: dict2[key2]})
    return dict1

if __name__ == '__main__':
    dict1 = {1: [2, 3],
             2: [0],
             4: [6]}
    dict2 = {1: [3, 4],
             3: [9, 8]}
    print(b(dict1, dict2))