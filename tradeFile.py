import time
from datetime import datetime

def appendTradeRecord(tradeStr):
    now = datetime.now()
    filename = "METX" + now.strftime("%Y") + now.strftime("%m") + now.strftime("%d")
    fhand = open(filename, "a")
    fhand.write(tradeStr + " Append@" + now.strftime("%H:%M:%S") + "\n")
    fhand.close()

def readtradeParasFromFile():
    fr = open("lastMETXrec.txt", 'r+')
    tradeParas = eval(fr.read())  # 读取的str转换为字典
    fr.close()
    print(tradeParas)
    if (input('Are you sure?') != 'y'):
        exit()
    return tradeParas

def savetradeParasToFile(tradeParas):
    fw = open("lastMETXrec.txt", 'w+')
    fw.write(str(tradeParas))  # 把字典转化为str
    fw.close()
    print('Save lastMETXrec.txt successfully!')
