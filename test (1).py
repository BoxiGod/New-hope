import pywaves as pw
import requests
import json
import time
status = False
idTicket = None


#config part
yourPrivateKey = ''
yourAddress = ''
betBlock = 3 #choose block when make a bet
node = 'https://nodes.wavesnodes.com'
node2 = 'http://localhost:6869'
node3 = 'https://api.vienna-node.eu'
GameAddress = pw.Address(privateKey = 'HAjYT2vhgcwTP4MmaCCKFgNmUuqtm98LQ6Hq9RwhFsgp')
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
    return GameAddress.dataTransaction(data, signer = yourPrivateKey, txFee = 10000000)

#send Waves, it's easy
def sendWaves(currHeight):
    yourAccount.sendWaves(recipient = pw.Address('3P9QNCmT3Q44zRYXBwKN3azBta9azGqrscm'), amount = 110000000, txFee = 10000000)
    print("Waves sent")

#searching for transaction with waves
def ticketId(currHeight):
    global idTicket
    print("Start searching for ticket...")
    txs = requests.get(node + '/transactions/address/3P9QNCmT3Q44zRYXBwKN3azBta9azGqrscm/limit/100').json()
    for data in txs:
        for item in data:
            if (item['sender'] == yourAddress) & (int(item['height']) > (int(currHeight) - 10)):
                print("Ticket found! ticketId = %s" % item['id'])
                idTicket = item['id']
                return item['id']
    return False

#Function, which returning current amount of blocks till win
def blocksToWin(currHeight):
    dataTx = requests.get(node + '/addresses/data/3P9QNCmT3Q44zRYXBwKN3azBta9azGqrscm').json()
    for data in dataTx:
            if data['key'] == 'heightToGetMoney':
                return data['value'] - currHeight

#This function return current potential winner
def currentWinner():
    dataTx = requests.get(node + '/addresses/data/3P9QNCmT3Q44zRYXBwKN3azBta9azGqrscm').json()
    for data in dataTx:
            if data['key'] == 'lastPayment':
                url = node + "/transactions/info/%s" % data['value']
                winTx = requests.get(url).json()
                return winTx['sender']

#Main, checking conditions to place a bet
def main():
    currHeight = pw.height()
    if blocksToWin(currHeight) <= betBlock:
        if currentWinner() != yourAddress:
            if ticketId(currHeight) == False:
                sendWaves(currHeight)
                while idTicket == None:
                    ticketId(currHeight)
                    time.sleep(1)
            else:
                currHeight = pw.height()
                winHeight = currHeight + 56
                sendData(paymId = idTicket, winHeight = winHeight)
                return print('data send, win height = %s, idTicket = %d' % (idTicket, winHeight))
        else: print("You are current potential winner")
    else:
        bToW = blocksToWin(currHeight)
        print ('It is only %d blocks till win' % bToW)
r = requests.get(node)
status = r.status_code == requests.codes.ok
if status == True:
    print("Connected to Waves Node, start working...")
    main()
else:
    r = requests.get(node2)
    status = r.status_code == requests.codes.ok
    if status == True:
        print("Connected to Waves Node, start working...")
        node = node2
        main()
    else:
        print("Connected to Waves Node, start working...")
        r = requests.get(node3)
        status = r.status_code == requests.codes.ok
        if status == True:
            node = node3
            main()
