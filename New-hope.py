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
nodes = ['http://localhost:6869', 'https://nodes.wavesnodes.com', 'https://api.vienna-node.eu', 'http://173.212.243.216:6869', 'http://138.197.155.74:6869']
GameAddress = pw.Address(privateKey = 'YnuT613AHFzSX7FQQQEDpa1xy6TYjMaxbuvVKgN87n4')
yourAccount = pw.Address(privateKey = yourPrivateKey)
attempts = 10 * len(nodes)

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
    for attempt in range(attempts):
        try:
            return GameAddress.dataTransaction(data, signer = yourPrivateKey, txFee = 500000)
        except requests.exceptions.RequestException:
            changeNode()
            continue
        else:
            break
    else:
        raise Exception("All attempts failed")

#send Waves, it's easy
def sendWaves():
    for attempt in range(attempts):
        try:
            data = yourAccount.sendWaves(recipient = pw.Address('3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw'), amount = 100500000, txFee = 100000)
        except requests.exceptions.RequestException:
            changeNode()
            continue
        else:
            break
    else:
        raise Exception("All attempts failed")
    logger.info("Waves sent, id = %s", data['id'])
    return data['id']

def withdraw():
    logger.info(GameAddress.sendWaves(recipient = pw.Address(yourAddress), amount = (GameAddress.balance() - 500000), txFee = 500000))
    logger.info("Withdraw success, check your balance")

#Function, which returning current amount of blocks till win
def blocksToWin():
    dataTx = getData()
    for data in dataTx:
            if data['key'] == 'heightToGetMoney':
                return data['value'] - getHeight()

def getData():
    numNodes = 0
    for attempt in range(attempts):
        try:
            return requests.get(nodes[numNodes] + '/addresses/data/3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw').json()
        except requests.exceptions.RequestException:
            logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            continue
        else:
            break
    else:
        raise Exception('All attempts failed')

#This function return current potential winner
def currentWinner():
    dataTx = getData()
    for data in dataTx:
            if data['key'] == 'lastPayment':
                return getTxInfo(data)['sender']

def getTxInfo(data):    
    numNodes = 0
    for attempt in range(attempts):
        try:
            url = nodes[numNodes] + "/transactions/info/%s" % data['value']
            return requests.get(url).json()
        except requests.exceptions.RequestException:
            logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            continue
        else:
            break
    else:
        raise Exception('All attempts failed')    

def isGame(currHeight, startRound):
    if (currHeight <= (startRound + 1240)) and blocksToWin() > 0:
        logger.info("Game is not over, check statements")
        return True
    else:
        logger.info("Round is over, waiting for next")
        return False

def changeNode():
    numNodes = 0
    r = requests.get(nodes[numNodes])
    status = r.status_code == requests.codes.ok
    while not status:
        logger.warning("Node %s is unavaliable, going to try next", nodes[numNodes])
        numNodes = (numNodes + 1) % (len(nodes) - 1)
        r = requests.get(nodes[numNodes])
        status = r.status_code == requests.codes.ok
    pw.setNode(node=nodes[numNodes])
    logger.info("Connected to %s", nodes[numNodes])


def getHeight():
    for attempt in range(attempts):
        try:
            return pw.height()
        except requests.exceptions.RequestException:
            changeNode()
            continue
        else:
            break
    else:
        raise Exception("All attempts failed")

#Main, checking conditions to place a bet
def main():
    currHeight = getHeight()
    currRound = (int((currHeight - gameStart) / 1440))
    startRound = gameStart + (currRound * 1440)
    if isGame(currHeight=currHeight, startRound=startRound):
        if blocksToWin() <= betBlock and currentWinner() != yourAddress:
            paymId = sendWaves()
            while currentWinner() != yourAddress:
                logger.info(sendData(paymId = paymId, winHeight = getHeight() + 14))
            logger.info("Bet done, waiting next turn...")
            time.sleep(360)
        else:
            if currentWinner() == yourAddress:
                logger.info("You are current potential winner")
            logger.info('It is only %d blocks till win', blocksToWin())
    else:
        if currentWinner() == yourAddress:
            logger.info("You win!")
            withdraw()
        while blocksToWin() <= 0:
            logger.info("Wait for next round")
            time.sleep(1)

def start():
    while True:
        main()
        time.sleep(0.2)

start()
