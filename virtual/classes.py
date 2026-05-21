import heapq
from dataclasses import dataclass

@dataclass(order=True)
class Event:
    # def __init__(self, time: float, gate: Gate):
    #     self.time = time
    #     self.gate = gate
    time: float
    gate: Gate

class Simulator:
    def __init__(self):
        self.queue: list[Event] = []
        self.current_time = 0.0

    def schedule(self, time: float, gate: Gate):
        heapq.heappush(self.queue, Event(time, gate))

    def run(self):
        while self.queue:
            event = heapq.heappop(self.queue)
            self.current_time = event.time
            event.gate.process(event.time, self)

class Gate:
    def __init__(self):
        self.outputs: list[Gate] = []

    def connect(self, gate: Gate):
        self.outputs.append(gate)

    def process(self, time: float, sim: Simulator):
        raise NotImplementedError("Cannot call process() on base Gate class")

    def propagate(self, time: float, sim: Simulator):
        for gate in self.outputs:
            sim.schedule(time, gate)
            
class Max(Gate):
    def __init__(self, num_inputs: int):
        super().__init__()
        self.num_inputs = num_inputs
        self.received_count = 0
        self.max_time = 0

    def process(self, time: float, sim: Simulator):
        self.received_count += 1
        self.max_time = max(self.max_time, time)
        
        if self.received_count == self.num_inputs:
            self.propagate(self.max_time, sim)
            
class Min(Gate):
    def __init__(self, num_inputs: int):
        super().__init__()
        self.received_count = 0
        
    def process(self, time: float, sim: Simulator):
        self.received_count += 1
        if self.received_count > 1:
            return
        self.propagate(time, sim)
        
class Exit(Gate):
    def process(self, time: float, sim: Simulator):
        print(f"Exit signal received at time {time}")