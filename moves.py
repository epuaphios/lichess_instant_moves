import requests
from bs4 import BeautifulSoup
import chess.pgn
import re
import io
import pymongo
import logging
import sys
from rcquerybuilder.builder import Builder

log = logging.getLogger().error

myclient = pymongo.MongoClient("mongodb://root:rootpassword@localhost:27017/")
mydb = myclient["chess"]
mycol = mydb["developers"]

id = sys.argv[1]

r = requests.get('https://lichess.org/' + id)
print('https://lichess.org/' + id)
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
moveSize=len(data["moves"])
qb = Builder(collection=None)
for i in range(moveSize):
    qb.field("moves."+str(i)+"").equals(data["moves"][i])
    # qb.field("Result").equals("w")

print(qb.get_query_list())
# for match in mycol.find(qb.get_query_list()):
#     print(match)

# db.developers.find({"moves.0": "d4","Result": "w"})
# moveSize=len(data["moves"])
# stringMove=""
# for i in range(moveSize):
#     stringMove += ""moves.""+str(i)+"" : "+data["moves"][i]+","
#     if i == moveSize-1:
#         stringMove += "moves."+str(i)+" : "+data["moves"][i]+" , ""Result: w"
# print(stringMove)
#
# pat = re.compile(stringMove, re.I)
# print(pat)
# match = mycol.find({pat}, {"moves": {'$slice': 3}})
# collection_cursor = eval(query)

# print (match)
#
# for match in mycol.find({ "moves" : { "$in" : data["moves"] } }):
