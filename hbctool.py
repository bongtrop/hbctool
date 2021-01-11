import hbc as hbcl
import hasm
import json

if __name__ == "__main__":
    hbc = hbcl.load(open("hbc/hbc74/example/index.android.bundle", "rb"))
    hbcl.dump(hbc, open("/tmp/index.android.bundle", "wb"))
    
    f = open("hbc/hbc74/example/index.android.bundle", "rb")
    a = f.read()
    f.close()
    f = open("/tmp/index.android.bundle", "rb")
    b = f.read()
    f.close()

    print(len(a), len(b))