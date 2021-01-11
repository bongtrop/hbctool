from hbc import parseFromFile
import hasm

if __name__ == "__main__":
    hbc = parseFromFile(open("hbc/hbc74/example/index.android.bundle", "rb"))
    hasm.dump(hbc, "output/test")