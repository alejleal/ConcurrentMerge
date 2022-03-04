from multiprocessing import BoundedSemaphore, Process, Lock, Array, Semaphore
from random import randint

"""
Nota: El almacen de cada productor se simula haciendo que el segmento buffer[i*CAP:(i + 1)*CAP] corresponda al productor i-ésimo.
Para añadir/consumir elementos de cada almacén se hace de manera modular. Por tanto, cada vez que se llega al final del almacén
de algun productor, se prosigue generando/consumiendo al inicio del segmento. De esta manera no es necesario mover todos los
numeros de sitio cada vez que se consume uno de ellos.
"""

CAP = 7
NPROD = 10
MAXPROD = 300

def producer(pid, buffer, empty, non_empty):
    last = 0
    lastSaved = 0
    for _ in range(MAXPROD):
        empty[pid].acquire()
        
        last += randint(0, 5)
        buffer[lastSaved + pid*CAP] = last

        lastSaved = (lastSaved + 1) % CAP

        non_empty[pid].release()

    # Cuando acaba de producir todo, va rellenando con -1
    for _ in range(CAP):
        empty[pid].acquire()
        buffer[lastSaved + pid*CAP] = -1
        non_empty[pid].release()

        lastSaved = (lastSaved + 1) % CAP

def merger(buffer, empty, non_empty, sorted_list):
    for s in non_empty:
        s.acquire()                                 # Espera al principio a que todos produzcan
    
    lastConsumed = [0]*NPROD    # Guarda la posición del ultimo elemento que ha consumido en el almacen de cada productor

    min_index = mindex([buffer[lastConsumed[i] + i*CAP] for i in range(NPROD)])     # Filtra los elementos del buffer tomando los que toquen de cada almacen de cada productor

    while max(buffer) > 1:
        sorted_list.append(buffer[lastConsumed[min_index] + min_index*CAP])
        lastConsumed[min_index] = (lastConsumed[min_index] + 1) % CAP               # Actualiza la posicion del ultimo consumido

        empty[min_index].release()
        non_empty[min_index].acquire()

        min_index = mindex([buffer[lastConsumed[i] + i*CAP] for i in range(NPROD)])

    print(sorted_list, len(sorted_list))

def mindex(buffer):
    pos_buffer = [e for e in buffer if e >= 0]      # Filtra los positivos
    if not pos_buffer:                              # Si no hay postivos devuelve -1
        return -1
    l = list(buffer)                                # Array no tiene un metodo llamado index 
    return l.index(min(pos_buffer))

def main():
    buffer = Array('i', [0]*NPROD*CAP)
    empty = []
    non_empty = []

    empty = [BoundedSemaphore(CAP) for _ in range(NPROD)]
    non_empty = [Semaphore(0) for _ in range(NPROD)]

    sorted_list = []

    lp = [Process(target=producer, args=(pid, buffer, empty, non_empty)) for pid in range(NPROD)]
    lp.append(Process(target=merger, args=(buffer, empty, non_empty, sorted_list)))

    for p in lp:
        p.start()

    for p in lp:
        p.join()

if __name__ == "__main__":
    main()