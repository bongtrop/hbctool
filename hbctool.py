from hbc import parseFromFile

def to_hasm():
    pass


if __name__ == "__main__":
    hbc = parseFromFile(open("hbc/hbc74/example/index.android.bundle", "rb"))
    functionName, paramCount, registerCount, symbolCount, inst, _ = hbc.getFunction(3819)
    
    