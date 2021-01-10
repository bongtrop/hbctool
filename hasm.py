from util import *

def to_hasm(f, hbc):
    stringCount = hbc.getStringCount()
    functionCount = hbc.getFunctionCount()

    for i in range(functionCount):
        functionName, paramCount, registerCount, symbolCount, inst, _ = hbc.getFunction(i)