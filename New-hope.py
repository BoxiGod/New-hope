import pywaves as pw
import requests
import json
import time
import logging
status = False
numNodes = 0

#logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('bot.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


#config part
gameStart = 1444767;
blocksPerRound = 1440;
blocksPerCompetition = 1240;
yourPrivateKey = ''
yourAddress = ''
betBlock = 2 #choose blocks till end when make a bet
nodes = ['https://nodes.wavesnodes.com', 'https://api.vienna-node.eu', 'http://173.212.243.216:6869', 'http://138.197.155.74:6869']
GameAddress = pw.Address(privateKey = 'YnuT613AHFzSX7FQQQEDpa1xy6TYjMaxbuvVKgN87n4')
yourAccount = pw.Address(privateKey = yourPrivateKey)


def sendData(paymId, winHeight):    #creating data to send
    data = [
        {
        "key": paymId,
        "type": "string",
        "value": "used"
        },
        {
        "key": "lastPayment",
        "type": "string",
        "value": paymId
        },
        {
        "key": "heightToGetMoney",
        "type": "integer",
        "value": winHeight
        },
    ]
    return GameAddress.dataTransaction(data, signer = yourPrivateKey, txFee = 500000)

#send Waves, it's easy
def sendWaves():
    data = yourAccount.sendWaves(recipient = pw.Address('3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw'), amount = 100500000, txFee = 100000)
    logger.info("Waves sent")
    return data['id']

def withdraw():
    yourAccount.sendWaves(recipient = pw.Address(yourAddress), amount = (GameAddress.balance() - 500000), txFee = 500000)
    logger.info("Withdraw success, check your balance")

#Function, which returning current amount of blocks till win
def blocksToWin():
    numNodes = 0
    while True:
        try:
            dataTx = requests.get(nodes[numNodes] + '/addresses/data/3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw').json()
        except requests.exceptions.RequestException:
            logger.info("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            continue
        break
    for data in dataTx:
            if data['key'] == 'heightToGetMoney':
                return data['value'] - pw.height()

#This function return current potential winner
def currentWinner():
    numNodes = 0
    while True:
        try:
            dataTx = requests.get(nodes[numNodes] + '/addresses/data/3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw').json()
        except requests.exceptions.RequestException:
            logger.info("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            continue
        break
    for data in dataTx:
            if data['key'] == 'lastPayment':
                url = nodes[numNodes] + "/transactions/info/%s" % data['value']
                numNodes = 0
                while True:
                    try:
                        winTx = requests.get(url).json()
                    except requests.exceptions.RequestException:
                        logger.info("Problem with %s, going to try next one node", nodes[numNodes])
                        numNodes = (numNodes + 1) % (len(nodes) - 1)
                        continue
                    break
                return winTx['sender']

def isGame(currHeight, startRound):
    if (currHeight <= (startRound + 1240)) and blocksToWin() > 0:
        logger.info("Game is not over, check statements")
        return True
    else:
        logger.info("Round is over, waiting for next")
        return False


#Main, checking conditions to place a bet
def main():
    currHeight = pw.height()
    currRound = (int((currHeight - gameStart) / 1440))
    startRound = gameStart + (currRound * 1440)
    if isGame(currHeight=currHeight, startRound=startRound):
        if currHeight == (startRound + 1240):
            paymId = sendWaves()
            while currentWinner() != yourAddress:
                logger.info(sendData(paymId = paymId, winHeight = pw.height()+14))
                time.sleep(0.3)
            exit()
        if blocksToWin(currHeight) <= betBlock and currentWinner() != yourAddress:
            paymId = sendWaves()
            while currentWinner() != yourAddress:
                logger.info(sendData(paymId = paymId, winHeight = pw.height()+14))
                time.sleep(0.3)
            time.sleep(180)
        else:
            if currentWinner() == yourAddress:
                logger.info("You are current potential winner")
            logger.info('It is only %d blocks till win', blocksToWin(0))
    else:
        if currentWinner() == yourAddress:
            logger.info("You win!")
            withdraw()
        while not (isGame(currHeight)):
            time.sleep(1)

def start():
    numNodes = 0
    while True:
        r = requests.get(nodes[numNodes])
        status = r.status_code == requests.codes.ok
        while not status:
            logger.info("Node %s is unavaliable, going to try next", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            r = requests.get(nodes[numNodes])
            status = r.status_code == requests.codes.ok
            time.sleep(0.1)
        pw.setNode(node=nodes[numNodes])
        logger.info("Connected to %s", nodes[numNodes])
        main()
        start()
        time.sleep(0.5)
#sendWaves(pw.height())
start()
#print(sendData(paymId="HSRkEHUX4dGmRXscjiy1FrSS4GuXw7YJJ5gqsJPXebQj", winHeight=(pw.height()+14)))
