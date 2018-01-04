import random
from vino.processors import runners
import pytest

def test_Runner_run_method_returns_processor_value(randstr):
    # function
    processor = lambda v,c: v
    r = runners.ProcessorRunner(processor)
    assert r.run(randstr)==randstr
    # object
    class p: 
        def run(self, value, context): return value
    processor = p()
    r = runners.ProcessorRunner(processor)
    assert r.run(randstr)==randstr

def test_RunnerStack_run_method_returns_value(randstr):
    processor = lambda v,c: v
    rs = runners.RunnerStack(None, processor)
    assert rs.run(randstr)==randstr


#def test_RunnerStack_run_method_calls_processors_in_order_of_addition():
#    length = 5
#    def create_fnc(i):
#        return lambda x: 
#    processors = [create_fnc(i) for i in range(length)]
#    rs = runners.RunnerStack(processors)
#
    

    

