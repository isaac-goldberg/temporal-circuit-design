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
            
class Min(Gate):
    """The Min gate takes any number of inputs. It outputs once any input goes high."""
    
    def __init__(self):
        super().__init__()
        
    async def process(self, _):
        if self.high: return
        await self.propagate()
            
class Max(Gate):
    """The Max gate takes any number of inputs. It outputs once all inputs are high."""
    
    def __init__(self, num_inputs: int):
        super().__init__()
        self.num_inputs = num_inputs
        self.received_count = 0
        
    async def process(self, _):
        self.received_count += 1
        if self.received_count == self.num_inputs: await self.propagate()
            
class AddConstant(Gate):
    """The AddConstant gate takes exactly one input event T and a constant K, and outputs at time T + K."""
    
    def __init__(self, K: float):
        super().__init__()
        self.K = K
        
    async def process(self, _):
        await asyncio.sleep(self.K)
        await self.propagate()
        
class Inhibit(Gate):
    """The Inhibit gate takes exactly two inputs: Td (data) and Tc (control), and outputs at time Td if and only if Td < Tc."""

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
            
class Exit(Gate):
    def __init__(self):
        super().__init__()
    
    async def process(self, _):
        print(f"time elapsed: {time.time() - circuit_start}")
        raise ExitProgram()

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
        