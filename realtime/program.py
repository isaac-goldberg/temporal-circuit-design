from classes import *
import asyncio

async def main():
    # path 1
    entry = EventScheduler()
    entry.schedule(1)
    entry.schedule(2)
    
    maxgate = MaxGate(2).connect(entry)
    delay = AddConstGate(0.5).connect(maxgate)
    
    # path 2
    entry2 = EventScheduler()
    entry2.schedule(1)
    
    delay2 = AddConstGate(0.5).connect(entry2)

    # see fastest path
    mingate = MinGate().connect(delay, delay2)
    Exit().connect(mingate)
    
    try:
        await simulation.start()
    except ExitSimulation:
        print("Program terminated")
            
asyncio.run(main())
