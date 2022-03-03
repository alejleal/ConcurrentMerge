from multiprocessing import BoundedSemaphore, Process, Lock, Value, Array, Semaphore
from random import randint

CAP = 7
NPROD = 10
MAXPROD = 300

def producer(pid, buffer, empty, non_empty, mutex):
    last = 0
    lastSaved = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        
        mutex.acquire()            
        last += randint(0, 5)
        buffer[lastSaved + pid*CAP] = last
        mutex.release()

        lastSaved = (lastSaved + 1) % CAP

        non_empty[pid].release()

    for _ in range(CAP):
        empty[pid].acquire()

        mutex.acquire()            
        buffer[lastSaved + pid*CAP] = -1
        mutex.release()

        non_empty[pid].release()

        lastSaved = (lastSaved + 1) % CAP


def merger(buffer, empty, non_empty, mutex, sorted_list):
    for s in non_empty:
        s.acquire()
    
    lastConsumed = [0]*NPROD

    min_index = mindex([buffer[lastConsumed[i] + i*CAP] for i in range(NPROD)])
    fin = min_index == -1

    while not fin:
        mutex.acquire()
        sorted_list.append(buffer[lastConsumed[min_index] + min_index*CAP])
        lastConsumed[min_index] = (lastConsumed[min_index] + 1) % CAP
        mutex.release()

        empty[min_index].release()
        non_empty[min_index].acquire()

        mutex.acquire()
        min_index = mindex([buffer[lastConsumed[i] + i*CAP] for i in range(NPROD)])
        fin = min_index == -1
        mutex.release()

    print(sorted_list[:-1], len(sorted_list))

def mindex(buffer):
    pos_buffer = [e for e in buffer if e >= 0]
    if not pos_buffer:
        return -1
    l = list(buffer)            # Array no tiene un metodo llamado index 
    return l.index(min(pos_buffer))

def main():
    buffer = Array('i', [0]*NPROD*CAP)
    empty = []
    non_empty = []
    mutex = Lock()

    for _ in range(NPROD):
        empty.append(BoundedSemaphore(CAP))
        non_empty.append(Semaphore(0))

    sorted_list = []

    lp = [Process(target=producer, args=(pid, buffer, empty, non_empty, mutex)) for pid in range(NPROD)]
    lp.append(Process(target=merger, args=(buffer, empty, non_empty, mutex, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

if __name__ == "__main__":
    main()