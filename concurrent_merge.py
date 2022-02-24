from multiprocessing import BoundedSemaphore, Process, Lock, Array, Semaphore
from random import randint


NPROD = 3
MAXPROD = 20

def produce(pid, buffer, empty, non_empty):
    last = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        print(f"Producing {pid}")
        try:
            last += randint(0, 5)
            buffer[pid] = last
        finally:
            non_empty[pid].release()
    buffer[pid] = -1

def merger(buffer, empty, non_empty, sorted_list):
    while any([e != -1 for e in buffer]):
        for ne in non_empty:
            ne.acquire()
        #non_empty[min_index].acquire()

        min_index = mindex(buffer)
        print(min_index)
        print(f"{buffer[0]} - {buffer[1]} - {buffer[2]}")

        try:
            print("Consumiendo...")
            sorted_list.append(buffer[min_index])
        finally:
            empty[min_index].release()
    print(sorted_list)

def mindex(buffer):
    l = len(buffer)
    if l == 0 or l == 1:
        return l - 1

    min_index = 0
    min_buffer = buffer[0]

    for i in range(1, l):
        if buffer[i] >= 0 and buffer[0] < min_buffer:
            min_index = i
            min_buffer = buffer[i]
    
    return min_index

def main():
    lp = []
    buffer = Array('i', [0]*NPROD)
    empty = []
    non_empty = []

    for _ in range(NPROD):
        empty.append(BoundedSemaphore(1))
        non_empty.append(Semaphore(0))

    sorted_list = []

    for pid in range(NPROD):
        lp.append(Process(target=produce, args=(pid, buffer, empty, non_empty)))

    lp.append(Process(target=merger, args=(buffer, empty, non_empty, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

if __name__ == "__main__":
    main()