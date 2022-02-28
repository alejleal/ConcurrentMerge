from multiprocessing import BoundedSemaphore, Process, Lock, Value, Array, Semaphore
from random import randint

NPROD = 5
MAXPROD = 20

def producer(pid, buffer, empty, full, buffer_lock):
    last = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        print(f"Produciendo {pid}")
 
        buffer_lock.acquire()
        last += randint(0, 5)
        buffer[pid] = last
        buffer_lock.release()

        full.release()
        print(f"Lleno {pid}")

    buffer[pid] = -1

def merger(buffer, empty, full, buffer_lock, sorted_list):
    while True:
        for _ in range(NPROD):
            full.acquire()

        buffer_lock.acquire()
        min_index = mindex(buffer)
        if min_index == -1:
            break
        print(f"Consumiendo {min_index}")
        sorted_list.append(buffer[min_index])
        buffer_lock.release()

        empty[min_index].release()
        print(f"Fusionado {min_index}")
        
        for _ in range(NPROD - 1):
            full.release()

    print(sorted_list, len(sorted_list))
    print(sorted_list[:-1])

def mindex(buffer):
    pos_buffer = [e for e in buffer if e >= 0]
    if not pos_buffer:
        return -1
    l = list(buffer)            # Array no tiene un metodo llamado index 
    return l.index(min(pos_buffer))

def main():
    lp = []
    buffer = Array('i', [0]*NPROD)
    empty = []
    full = Semaphore(NPROD)
    buffer_lock = Lock()

    for _ in range(NPROD):
        empty.append(Semaphore(1))

    sorted_list = []

    for pid in range(NPROD):
        lp.append(Process(target=producer, args=(pid, buffer, empty, full, buffer_lock)))
    lp.append(Process(target=merger, args=(buffer, empty, full, buffer_lock, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

if __name__ == "__main__":
    main()