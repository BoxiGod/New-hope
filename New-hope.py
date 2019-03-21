import pywaves as pw
import requests
import json
import time
import logging
status = False

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
betBlock = 3 #choose blocks till end when make a bet
node = 'https://nodes.wavesnodes.com'
node2 = 'http://localhost:6869'
node3 = 'https://api.vienna-node.eu'
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
    yourAccount.sendWaves(recipient = pw.Address(yourAddress), amount = (GameAddress.balance() - 100000), txFee = 100000)
    logger.info("Withdraw success, check your balance")

#Function, which returning current amount of blocks till win
def blocksToWin(currHeight):
    dataTx = requests.get(node + '/addresses/data/3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw').json()
    for data in dataTx:
            if data['key'] == 'heightToGetMoney':
                return data['value'] - currHeight

#This function return current potential winner
def currentWinner():
    dataTx = requests.get(node + '/addresses/data/3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw').json()
    for data in dataTx:
            if data['key'] == 'lastPayment':
                url = node + "/transactions/info/%s" % data['value']
                winTx = requests.get(url).json()
                return winTx['sender']

def isGame(currHeight):
    global gameStart
    currRound = (int((currHeight - gameStart) / 1440))
    startRound = gameStart + (currRound * 1440)
    if (currHeight <= (startRound + 1240)) and blocksToWin(currHeight) > 0:
        logger.info("Game is not over, check statements")
        return True
    else:
        logger.info("Round is over, waiting for next")
        return False
    

#Main, checking conditions to place a bet
def main():
    currHeight = pw.height()
    global betBlock
    global gameStart
    currRound = (int((currHeight - gameStart) / 1440))
    startRound = gameStart + (currRound * 1440)
    if isGame(currHeight):
        if currHeight == (startRound + 1239):
            paymId = sendWaves()
            while currentWinner() != yourAddress:
                logger.info(sendData(paymId = paymId, winHeight = pw.height()+14))
                time.sleep(0.3)
            exit()
        if blocksToWin(currHeight) <= betBlock and currentWinner() != yourAddress:
            currHeight = pw.height()
            paymId = sendWaves()
            while currentWinner() != yourAddress:
                logger.info(sendData(paymId = paymId, winHeight = pw.height()+14))
                time.sleep(0.3)
            time.sleep(180)
        else:
            if currentWinner() == yourAddress:
                logger.info("You are current potential winner")
                logger.info('It is only %d blocks till win', blocksToWin(currHeight))
            logger.info('It is only %d blocks till win', blocksToWin(currHeight))
    else:
        if currentWinner() == yourAddress:
            logger.info("You win!")
            withdraw()
        while not (isGame(currHeight)):
            time.sleep(1)

def start():
    global node
    while True:
        r = requests.get(node)
        status = r.status_code == requests.codes.ok
        if status == True:
            pw.setNode(node = node, chain = 'mainnet')
            logger.info("Connected to Waves Node, start working...")
            main()
        else:
            r = requests.get(node2)
            status = r.status_code == requests.codes.ok
            if status == True:
                pw.setNode(node = node, chain = 'mainnet')
                logger.info("Connected to Waves Node, start working...")
                node = node2
                main()
            else:
                logger.info("Connected to Waves Node, start working...")
                r = requests.get(node3)
                status = r.status_code == requests.codes.ok
                if status == True:
                    pw.setNode(node = node, chain = 'mainnet')
                    node = node3
                    main()
                else:
                    start()
        time.sleep(0.5)
#start()
