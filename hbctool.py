from hbc import parseFromFile

if __name__ == "__main__":
    hbc = parseFromFile(open("hbc/hbc74/example/index.android.bundle", "rb"))
    functionName, paramCount, inst = hbc.getFunction(3845)
    print(f"Function {functionName} (paramCount: {paramCount})")
    