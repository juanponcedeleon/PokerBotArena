"""How much computation fits in the 1 ms decision budget."""
import json
import random
import time

import eval7

from common import CARDS, c

rng = random.Random(1)
hands = [rng.sample(CARDS, 7) for _ in range(20000)]
t = time.perf_counter_ns()
for h in hands:
    eval7.evaluate(h)
dt = (time.perf_counter_ns() - t) / len(hands)
print(f"eval7.evaluate 7 cards: {dt:.0f} ns/call  -> ~{int(1_000_000 / dt)} evals per ms")

hands5 = [h[:5] for h in hands]
t = time.perf_counter_ns()
for h in hands5:
    eval7.evaluate(h)
dt5 = (time.perf_counter_ns() - t) / len(hands)
print(f"eval7.evaluate 5 cards: {dt5:.0f} ns/call")

board = [c('Qs'), c('7d'), c('2c'), c('Th'), c('4s')]
exp = c('Qh')
unknown = [x for x in CARDS if x not in board and x != exp][:45]
t = time.perf_counter_ns()
for _ in range(200):
    for u in unknown:
        eval7.evaluate([exp, u] + board)
dt45 = (time.perf_counter_ns() - t) / 200
print(f"45-card hidden enumeration, one opponent, river: {dt45 / 1000:.0f} us")

# flop: 45 hidden x 45 turn x 44 river is too much; 45 hidden x ~100 runouts
t = time.perf_counter_ns()
rest = [x for x in CARDS if x not in board[:3] and x != exp]
for _ in range(5):
    for u in rest[:45]:
        for _ in range(100):
            tr = rng.sample(rest, 2)
            eval7.evaluate([exp, u] + board[:3] + tr)
dtflop = (time.perf_counter_ns() - t) / 5
print(f"45 hidden x 100 runouts on the flop: {dtflop / 1000:.0f} us  (too slow for 1 ms)")

mem = {str(i): {"vpip": 10, "pfr": 3, "shows": [["Qh", "7d"]] * 5, "hist": [1, 2, 3] * 20}
       for i in range(8)}
b = json.dumps(mem).encode()
t = time.perf_counter_ns()
for _ in range(2000):
    json.loads(b)
    json.dumps(mem).encode()
print(f"json memory round trip ({len(b)} bytes): {(time.perf_counter_ns() - t) / 2000 / 1000:.0f} us")
