import asyncio
import time

circuit_start = 0

class ExitProgram(Exception):
    pass

"""Base class for all gates."""
class Gate:
    def __init__(self):
        self.outputs: list[Gate] = []
        self.high = False
    
    def connect(self, gate: Gate):
        self.outputs.append(gate)
        
    async def process(self, _):
        raise NotImplementedError("process() cannot be called on base Gate class")
    
    async def propagate(self):
        self.high = True
        for output in self.outputs:
            await output.process(self)
            
"""The Min gate takes any number of inputs. It outputs once any input goes high."""
class Min(Gate):    
    def __init__(self):
        super().__init__()
        
    async def process(self, _):
        if self.high: return
        await self.propagate()

"""The Max gate can take any number of input events, but it must be told the number of inputs to wait for. It outputs once all inputs are high."""
class Max(Gate):
    def __init__(self, num_inputs: int):
        super().__init__()
        self.num_inputs = num_inputs
        self.received_count = 0
        
    async def process(self, _):
        self.received_count += 1
        if self.received_count == self.num_inputs: await self.propagate()
            
"""The AddConstant gate takes exactly one input event T and a constant K, and outputs at time T + K."""
class AddConstant(Gate):    
    def __init__(self, K: float):
        super().__init__()
        self.K = K
        
    async def process(self, _):
        await asyncio.sleep(self.K)
        await self.propagate()
        
"""The Inhibit gate takes exactly two inputs: Td (data) and Tc (control), and outputs at time Td if and only if Td < Tc."""
class Inhibit(Gate):
    def __init__(self):
        super().__init__()
        self.td = None
        self.tc = None
        self.tc_arrived = False
        self.high
        
    def connect(self):
        raise NotImplementedError("The Inhibit gate doesn't use the connect() method. Use connect_td() and connect_tc()")
        
    def connect_td(self, gate: Gate):
        self.td = gate
        
    def connect_tc(self, gate: Gate):
        self.tc = gate
        
    async def process(self, gate: Gate):
        if self.tc_arrived or self.high: return
        
        if gate == self.tc:
            self.tc_arrived = True
        elif gate == self.td:
            self.propagate()
        else:
            raise AssertionError("tried to propagate inhibit gate from an event that isn't the Td or Tc for this gate")

"""Connect other gates to an Exit gate to singify the end of the circuit. Once an Exit gate receives a signal, it terminates the program."""
class Exit(Gate):
    def __init__(self):
        super().__init__()
    
    async def process(self, _):
        print(f"time elapsed: {time.time() - circuit_start}")
        raise ExitProgram()

"""Use the Entry gate to provide initial event signals, with delays, to the circuit."""
class Entry(Gate):
    def __init__(self):
        super().__init__()
        self.scheduled_events = []
    
    def schedule(self, delay: float):
        self.scheduled_events.append(delay)
        
    async def send_signal(self, delay: float):
        await asyncio.sleep(delay)
        await self.propagate()
        
    async def start(self):
        global circuit_start
        circuit_start = time.time()
        tasks = [asyncio.create_task(self.send_signal(delay)) for delay in self.scheduled_events]
        await asyncio.gather(*tasks)
        