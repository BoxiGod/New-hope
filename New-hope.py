import pywaves as pw
import requests
import json
import time
import logging
status = False
idTicket = None

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
node = 'https://nodes.wavesnodes.com'
node2 = 'http://localhost:6869'
node3 = 'https://api.vienna-node.eu'
GameAddress = pw.Address(privateKey = 'YnuT613AHFzSX7FQQQEDpa1xy6TYjMaxbuvVKgN87n4')
yourAccount = pw.Address(privateKey = yourPrivateKey)


def sendData(paymId, winHeight):    #creating data to send
    data = [
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
      {
        "key": paymId,
        "type": "string",
        "value": "used"
      }
    ]
    return GameAddress.dataTransaction(data, signer = yourPrivateKey, txFee = 100000)

#send Waves, it's easy
def sendWaves(currHeight):
    yourAccount.sendWaves(recipient = pw.Address('3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw'), amount = 100500000, txFee = 100000)
    logger.info("Waves sent")

#searching for transaction with waves
def ticketId(currHeight):
    global idTicket
    logger.info("Start searching for ticket...")
    txs = requests.get(node + '/transactions/address/3P7qcbeYEnD9B7GPHwkhNv2pmDZTiYwVDLw/limit/100').json()
    for data in txs:
        for item in data:
            if (item['sender'] == yourAddress) & (int(item['height']) > (int(currHeight) - 10)):
                print("Ticket found! ticketId = %s" % item['id'])
                idTicket = item['id']
                return item['id']
    return False

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
    #print("currRound = %d" % currRound)
   # print("start round = %d" % startRound)
    if (currHeight <= (startRound + 1240)) and blocksToWin(currHeight) > 0:
        logger.info("Game is not over, check statements")
        return True
    else:
        logger.info("Round is over, waiting for next")
        return False


#Main, checking conditions to place a bet
def main():
    currHeight = pw.height()
    global idTicket
    global betBlock
    if isGame(currHeight):
        if blocksToWin(currHeight) <= betBlock:
            if currentWinner() != yourAddress:
                if ticketId(currHeight) == False:
                    sendWaves(currHeight)
                    while idTicket == None:
                        ticketId(currHeight)
                        time.sleep(0.3)
                else:
                    currHeight = pw.height()
                    winHeight = currHeight + 13
                    sendData(paymId = idTicket, winHeight = winHeight)
                    logger.info('data send, win height = %s, idTicket = %d', idTicket, winHeight)
                    idTicket = None
            else:
                logger.info("You are current potential winner")
        else:
            logger.info('It is only %d blocks till win', bToW)
    else:
        while not (isGame(currHeight)):
            time.sleep(1)
        
while True:
    r = requests.get(node)
    status = r.status_code == requests.codes.ok
    if status == True:
        logger.info("Connected to Waves Node, start working...")
        main()
    else:
        r = requests.get(node2)
        status = r.status_code == requests.codes.ok
        if status == True:
            logger.info("Connected to Waves Node, start working...")
            node = node2
            main()
        else:
            logger.info("Connected to Waves Node, start working...")
            r = requests.get(node3)
            status = r.status_code == requests.codes.ok
            if status == True:
                node = node3
                main()
    time.sleep(1)
"""
print("Start program")
isGame();
"""
