import pywaves as pw
import requests
import json
import logging
import time
import re


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('bot.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


pw.setNode(node='https://nodes.wavesnodes.com', chain='mainnet')
nodes = ['https://nodes.wavesnodes.com', 'https://api.vienna-node.eu', 'http://45.33.22.96:6869', 'http://207.180.224.213:6869', 'http://83.135.237.51:6869']
attempts = 10 * len(nodes)
gameStart = 1824280;
blocksPerRound = 1460;
blocksPerCompetition = 1450;
betBlock = 4
numNodes = 0
previousRound = 58
PlayingAccount = pw.Address(privateKey = '')
yourAddress = ''
rush = 0


def currentWinner():
    tr = 0
    global numNodes
    for attempt in range(attempts):
        while True:
            try:
                firstW = ''
                secondW = ''
                Data = getData(numNodes)
                startPos = Data['value'].find('-')
                firstW = Data['value'][startPos+1:startPos+36]
                Data = getData(numNodes + 1)
                startPos = Data['value'].find('-')
                secondW = Data['value'][startPos+1:startPos+36]
                tr = tr + 1
                if tr == 10:
                    return firstW
                if firstW == secondW:
                    return firstW
            except Exception as e:
                logger.error(e)
                numNodes = (numNodes + 1) % (len(nodes) - 1)
                break
            

def getHeight():
    x = 0
    global numNodes
    for attempt in range(attempts):
        try:
            pw.setNode(node=nodes[numNodes])
            height_1 = pw.height()
            pw.setNode(node=nodes[numNodes + 1])
            height_2 = pw.height()
            return max(height_1, height_2)
        except Exception as e:
            logger.error(e)
            logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            continue
        else:
            break
    else:
        raise Exception("All attempts failed")


def getData(numNodes):
    for attempt in range(attempts):
        try:
            return requests.get(nodes[numNodes] + '/addresses/data/3PDtyStFHhEF5LSqPi4amUUAW6KQQQhNaR7/RoundsSharedState').json()
        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError) as e:
            logger.error(e)
            logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            pw.setNode(node=nodes[numNodes])
            continue
        else:
            break
    else:
        raise Exception('All attempts failed')


def blocksToWin():
    return int(getData(numNodes)['value'][0:7])-int(getHeight())


def isGame():
    currHeight = getHeight()
    currRound = int((currHeight - gameStart) / blocksPerRound)
    startRound = gameStart + (currRound * blocksPerRound)
    if (currHeight <= (startRound + blocksPerCompetition)) and blocksToWin() > 0:
        if startRound + 1435 <= currHeight:
            logger.info("15 blocks left till end")
            while startRound + 1449 != currHeight:
                logger.info("Blocks left: %s", str((startRound + 1450) - currHeight))
                currHeight = getHeight()
                time.sleep(0.3)
            makeBet()
            while True:
                makeBet()
        logger.info("Game is not over, check statements")
        return True
    else:
        logger.info("Round is over, waiting for next")
        return False


def makeBet():
    global numNodes
    try:
        tx = PlayingAccount.invokeScript('3PDtyStFHhEF5LSqPi4amUUAW6KQQQhNaR7', 'move', params = [], txFee = 1000000, payments = [ { "amount": 100*100, "assetId": "4uK8i4ThRGbehENwa6MxyLtxAjAo1Rj9fduborGExarC" } ])
        try:
            logger.error(tx['error'])
            logger.error(tx)
            logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            pw.setNode(node=nodes[numNodes])
            return False
        except Exception as e:
            logger.info(tx)
            return True
    except Exception as e:
        logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
        numNodes = (numNodes + 1) % (len(nodes) - 1)
        pw.setNode(node=nodes[numNodes])
        logger.error(e)
        return False


def main():
    if isGame():
        curWin = currentWinner()
        blocksTillWin = blocksToWin()
        if curWin == "3PDThJ9VZ7UJe6JHJXLuvvtcim4Thmd45TL" and rush == 1:
            while True:
                if makeBet():
                    logger.info("bet done")
                    time.sleep(180)
                    break
        if blocksTillWin <= betBlock and curWin != yourAddress:
            time.sleep(5)
            curWin = currentWinner()
            blocksTillWin = blocksToWin()
            if blocksTillWin <= betBlock and curWin != yourAddress:
                while True:
                    if makeBet():
                        logger.info("bet done")
                        time.sleep(180)
                        break
            else:
                if curWin == yourAddress:
                    logger.info("You are current potential winner")
                logger.info('Not time yet to bet, blocks till win: %s', str(blocksTillWin))
        else:
            if curWin == yourAddress:
                logger.info("You are current potential winner")
            logger.info('Not time yet to bet, blocks till win: %s', str(blocksTillWin))
    else:
        global previousRound
        if currentWinner() == yourAddress:
            logger.info("You win!")
            withdraw = PlayingAccount.invokeScript('3PDtyStFHhEF5LSqPi4amUUAW6KQQQhNaR7', 'withdraw', params = [{"type": "integer", "value": previousRound+1}], payments = [])
            logger.info(withdraw)
            time.sleep(1200)
        previousRound = previousRound + 1
        start()


def getRound(numNodes):
    for attempt in range(attempts):
        try:
            data = requests.get(nodes[numNodes] + '/addresses/data/3PDtyStFHhEF5LSqPi4amUUAW6KQQQhNaR7').json()
            temp = re.findall(r'\d+', data[len(data)-1]['key'])
            res = list(map(int, temp))
            return int(res[0])
        except Exception as e:
            logger.error(e)
            logger.warning("Problem with %s, going to try next one node", nodes[numNodes])
            numNodes = (numNodes + 1) % (len(nodes) - 1)
            pw.setNode(node=nodes[numNodes])
            continue
        else:
            break
    else:
        raise Exception('All attempts failed')


def start():
    while not isGame():
        currHeight = getHeight()
        currRound = int((currHeight - gameStart) / blocksPerRound)
        if currRound != previousRound:
            time.sleep(10)
            if blocksToWin() < 0:
                while True:
                    if makeBet():
                        time.sleep(300)
                        logger.info('made initial bet')
                        break
        time.sleep(30)
    while True:
        main()
        time.sleep(0.05)
start()
