from classes import *

# path 1
entry = EventScheduler().schedule(1, 2)

maxgate = MaxGate().connect(entry)
delay = AddConstGate(0.5).connect(maxgate)

# path 2
entry2 = EventScheduler().schedule(1)

delay2 = AddConstGate(0.5).connect(entry2)

# see fastest path
mingate = MinGate().connect(delay, delay2)
Exit().connect(mingate)

simulation.start()
