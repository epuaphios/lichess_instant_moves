import requests
from bs4 import BeautifulSoup
import chess.pgn
import re
import io
import pymongo
import logging
from collections import Counter
from Builder import Builder

log = logging.getLogger().error

myclient = pymongo.MongoClient("mongodb://root:rootpassword@localhost:27017/")
mydb = myclient["chess"]
mycol = mydb["developers"]
side = 'w'

r = requests.get('https://lichess.org/ViJO1Cvc')
soup = BeautifulSoup(r.content, 'html.parser')

all_tables=soup.find_all('div', {'class':'pgn'} )
output = str(all_tables[0].text).splitlines(0)[-1]
pgn = io.StringIO(output)
node = chess.pgn.read_game(pgn)
data = node.headers
data["moves"] = []
while node.variations:
    next_node = node.variation(0)
    data["moves"].append(
        re.sub("\{.*?\}", "", node.board().san(next_node.move)))
    node = next_node
moveSize = len(data["moves"])
sliceSize = moveSize+1
print(sliceSize)
qb = Builder(collection=None)

for i in range(moveSize):
    qb.field("moves."+str(i)+"").equals(data["moves"][i])
qb.field("Result").equals(side)
# qb.find()


print(qb.get_query_list())
listEndMoves = []
for match in mycol.find(qb.get_query_list(), {"moves": {"$slice": sliceSize}, "_id": 0, "Result": 0}):
    array = match.get("moves")
    # print(array)
    if len(array) == sliceSize:
        listEndMoves.append(array[sliceSize-1])
        # print(array[sliceSize-1])
print(Counter(listEndMoves).most_common(3))
