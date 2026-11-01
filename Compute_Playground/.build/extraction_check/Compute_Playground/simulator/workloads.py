"""Private random generator: the same seed always yields the same ordered workload."""
import random
from .engine import Task,TENANTS

def seeded_workload(seed=7,count=30):
    if not isinstance(seed,int) or not isinstance(count,int) or not 1<=count<=1000:
        raise ValueError('Integer seed and count from 1 to 1000 required')
    rng=random.Random(seed)
    arrival=0
    tasks=[]
    for i in range(count):
        arrival+=rng.choice([0,0,5,10,20])
        tasks.append(Task(f'S{seed}-{i+1:03}',TENANTS[i%2],rng.choice([1,2,3,4]),rng.choice([1,2,3,4]),rng.choice(['low','medium','high']),rng.choice([40,80,120,200,320,400]),arrival))
    return tasks
