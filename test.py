if __name__ == '__main__':
    D = {1: 100, 2: 200, 3: 300}
    print(D.keys())
    print(1 in D.keys())
    print(2 in D.keys())
    x = int(input("input:"))
    if x in D.keys():
        print(D[x])
    else:
        print("no")
