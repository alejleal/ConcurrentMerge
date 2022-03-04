from multiprocessing import BoundedSemaphore, Process, Lock, Array, Semaphore
from random import randint

NPROD = 10
MAXPROD = 200

def producer(pid, buffer, empty, non_empty):
    last = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        
        last += randint(0, 5)
        buffer[pid] = last

        non_empty[pid].release()

    empty[pid].acquire()
    buffer[pid] = -1
    non_empty[pid].release()    


def merger(buffer, empty, non_empty, sorted_list):
    for s in non_empty:
        s.acquire()                                 # Espera al principio a que todos produzcan
    
    min_index = mindex(buffer)
    # fin = min_index == -1

    while max(buffer) > -1:                        # Como los numeros generados son positivos, si el maximo es -1 entonces significa que todos han acabado
        sorted_list.append(buffer[min_index])

        empty[min_index].release()
        non_empty[min_index].acquire()

        min_index = mindex(buffer)
        # fin = min_index == -1                       # Comprueba si todos han terminado

    print(sorted_list, len(sorted_list))

def mindex(buffer):
    pos_buffer = [e for e in buffer if e >= 0]      # Filtra los positivos
    if not pos_buffer:                              # Si no hay postivos devuelve -1
        return -1
    l = list(buffer)                                # Array no tiene un metodo llamado index 
    return l.index(min(pos_buffer))

def main():
    buffer = Array('i', [0]*NPROD)
    empty = []
    non_empty = []

    empty = [BoundedSemaphore(1) for _ in range(NPROD)]
    non_empty = [Semaphore(0) for _ in range(NPROD)]

    sorted_list = []

    lp = [Process(target=producer, args=(pid, buffer, empty, non_empty)) for pid in range(NPROD)]
    lp.append(Process(target=merger, args=(buffer, empty, non_empty, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

    print(sorted_list)

if __name__ == "__main__":
    main()