from classes import *
import asyncio

async def main():
    # path 1
    entry = EntryGate()
    entry.schedule(1)
    entry.schedule(2)
    
    maxgate = MaxGate(2)
    entry.connect(maxgate)
    delay = AddConstGate(0.5)
    maxgate.connect(delay)
    
    # path 2
    entry2 = EntryGate()
    entry2.schedule(1)
    
    delay2 = AddConstGate(0.5)
    entry2.connect(delay2)

    # see fastest path
    mingate = MinGate()
    exit = ExitGate()
    
    delay.connect(mingate)
    delay2.connect(mingate)
    mingate.connect(exit)
    
    try:
        await simulation.start()
    except ExitSimulation:
        print("Program terminated")
            
asyncio.run(main())
