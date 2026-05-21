from classes import *

sim = Simulator()

max_gate = Min(2)
exit = Exit()

max_gate.connect(exit)

sim.schedule(1.0, max_gate)
sim.schedule(2.0, max_gate)

sim.run()
