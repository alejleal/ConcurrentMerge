from multiprocessing import BoundedSemaphore, Process, Lock, Value, Array, Semaphore
from random import randint

NPROD = 5
MAXPROD = 20

def producer(pid, buffer, empty, full, ready, ready_lock, buffer_lock):
    last = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        try:
            last += randint(0, 5)

            buffer_lock.acquire()            
            buffer[pid] = last
            buffer_lock.release()

        finally:
            ready_lock.acquire()
            try:
                if ready.value + 1 == NPROD:
                    full.release()
                ready.value += 1
            finally:
                ready_lock.release()
    buffer[pid] = -1

def merger(buffer, empty, full, ready, ready_lock, buffer_lock, sorted_list):
    while any([e != -1 for e in buffer]):
        full.acquire()

        buffer_lock.acquire()
        min_index = mindex(buffer)
        if min_index != -1:
            sorted_list.append(buffer[min_index])
        buffer_lock.release()

        ready_lock.acquire()
        ready.value -= 1
        ready_lock.release()
        
        empty[min_index].release()
    print(sorted_list)

def mindex(buffer):
    if not [e for e in buffer if e >= 0]:
        return -1
    l = list(buffer)
    return l.index(min([e for e in buffer if e >= 0]))

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
    ready = Value('i', 0)
    empty = []
    full = Semaphore(1)
    ready_lock = BoundedSemaphore(1)
    buffer_lock = Lock()

    for _ in range(NPROD):
        empty.append(Lock())

    sorted_list = []

    for pid in range(NPROD):
        lp.append(Process(target=producer, args=(pid, buffer, empty, full, ready, ready_lock, buffer_lock)))
    lp.append(Process(target=merger, args=(buffer, empty, full, ready, ready_lock, buffer_lock, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

if __name__ == "__main__":
    main()