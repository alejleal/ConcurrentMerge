from multiprocessing import BoundedSemaphore, Process, Lock, Value, Array, Semaphore
from random import randint

NPROD = 20
MAXPROD = 200

def producer(pid, buffer, empty, non_empty, mutex):
    last = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        
        mutex.acquire()            
        last += randint(0, 5)
        buffer[pid] = last
        mutex.release()

        non_empty[pid].release()

    # empty[pid].acquire()
    # mutex.acquire()            
    buffer[pid] = -1
    # mutex.release()
    # non_empty[pid].release      


def merger(buffer, empty, non_empty, mutex, sorted_list):
    for s in non_empty:
        s.acquire()

    while True:
        mutex.acquire()
        min_index = mindex(buffer)
        if min_index == -1:
            break
        sorted_list.append(buffer[min_index])
        mutex.release()

        empty[min_index].release()
        non_empty[min_index].acquire()

    print(sorted_list[:-1], len(sorted_list))

def mindex(buffer):
    pos_buffer = [e for e in buffer if e >= 0]
    if not pos_buffer:
        return -1
    l = list(buffer)            # Array no tiene un metodo llamado index 
    return l.index(min(pos_buffer))

    l = len(buffer)
    if l == 0 or l == 1:
        return l - 1

    if max(buffer) < 0:
        return -1

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
    mutex = Lock()

    for _ in range(NPROD):
        empty.append(BoundedSemaphore(1))
        non_empty.append(Semaphore(0))

    sorted_list = []

    for pid in range(NPROD):
        lp.append(Process(target=producer, args=(pid, buffer, empty, non_empty, mutex)))
    lp.append(Process(target=merger, args=(buffer, empty, non_empty, mutex, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

if __name__ == "__main__":
    main()