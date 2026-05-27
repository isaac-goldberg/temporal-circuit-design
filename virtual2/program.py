from classes import *

# path 1
entry = EventScheduler()
entry.schedule(1)
entry.schedule(2)

maxgate = MaxGate().connect(entry)
delay = AddConstGate(0.5).connect(maxgate)

# path 2
entry2 = EventScheduler()
entry2.schedule(1)

delay2 = AddConstGate(0.5).connect(entry2)

# see fastest path
mingate = MinGate().connect(delay, delay2)
Exit().connect(mingate)

simulation.start()
