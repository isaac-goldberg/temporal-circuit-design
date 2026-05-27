class Simulation:
    def __init__(self):
        self.entry_gates: list[EventScheduler] = []
        
    def add_entry(self, gate: EventScheduler):
        self.entry_gates.append(gate)
        
    def start(self):
        for gate in self.entry_gates:
            gate.start()
        
simulation = Simulation()

"""Base class for all gates."""
class Gate:
    def __init__(self):
        self.outputs: list[Gate] = []
        self.high = False
    
    """Connect another gate (or gates) to be an input to this gate. Returns this gate to allow for chaining."""
    def connect(self, *other_gates: Gate):
        for other_gate in other_gates: 
            other_gate.outputs.append(self)
        return self
        
    def process(self, _gate, _t):
        raise NotImplementedError("process() cannot be called on base Gate class")
    
    def propagate(self, t: float):
        self.high = True
        for output in self.outputs:
            output.process(self, t)
            
"""The Min gate takes any number of inputs. It outputs once any input goes high."""
class MinGate(Gate):
    def __init__(self, num_inputs: int = 2):
        super().__init__()
        self.num_inputs = num_inputs
        self.received_count = 0
        self.min_time = float('inf')
        
    def process(self, _, t: float):
        if t < self.min_time:
            self.min_time = t
        
        self.received_count += 1
        if self.received_count == self.num_inputs:
            self.propagate(self.min_time)

"""The Max gate can take any number of input events, but it must be told the number of inputs to wait for. It outputs once all inputs are high."""
class MaxGate(Gate):
    def __init__(self, num_inputs: int = 2):
        super().__init__()
        self.num_inputs = num_inputs
        self.received_count = 0
        self.max_time = 0
        
    def process(self, _, t: float):
        if t > self.max_time:
            self.max_time = t
            
        self.received_count += 1
        if self.received_count == self.num_inputs:
            self.propagate(self.max_time)
            
"""The AddConst gate must be initialized with a constant float K, takes exactly one input event T, and outputs at time T + K."""
class AddConstGate(Gate):    
    def __init__(self, K: float):
        super().__init__()
        self.K = K
        
    def process(self, _, t: float):
        self.propagate(t + self.K)
        
"""The Inhibit gate takes exactly two inputs: Td (data) and Tc (control), and outputs at time Td if and only if Td < Tc."""
class InhibitGate(Gate):
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
        
    def process(self, gate: Gate, t: float):
        if self.tc_arrived or self.high: return
        
        if gate == self.tc:
            self.tc_arrived = True
        elif gate == self.td:
            self.propagate(t)
        else:
            raise AssertionError("tried to propagate inhibit gate from an event that isn't the Td or Tc for this InhibitGate")

"""Connect other gates to an Exit gate to signify the end of the circuit. Once an Exit gate receives a signal, it terminates the program."""
class Exit(Gate):
    def __init__(self):
        super().__init__()
    
    def process(self, _, t: float):
        print(f"exit reached at time: {t}")

"""Use the EventSchedulerGate to provide initial event signals, with delays, to the circuit."""
class EventScheduler(Gate):
    def __init__(self):
        super().__init__()
        self.scheduled_events = []
        simulation.add_entry(self)
    
    def schedule(self, delay: float):
        self.scheduled_events.append(delay)
        
    def start(self):
        for delay in self.scheduled_events:
            self.propagate(delay)
        