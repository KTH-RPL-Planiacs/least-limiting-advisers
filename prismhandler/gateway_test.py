from py4j.java_gateway import JavaGateway
import time

gateway = JavaGateway()
prism_handler = gateway.entry_point.getPrismHandler()

start_time = time.time()
prism_handler.loadModelFile('../examples/test_game.prism')
start_time = time.time()
result = prism_handler.checkProperty('<< p1,p2 >> Pmax =? [F \"accept\"]')
print("TOOK", time.time()-start_time)

res_copy = []
for res in result:
    res_copy.append(res)

print(res_copy)
