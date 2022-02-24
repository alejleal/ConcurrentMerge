from multiprocessing import BoundedSemaphore, Process, Value, Lock

N = 8

def task(common, tid, b_semaphore):
    a = 0
    for i in range(100):
        print(f'{tid}-{i}: Non-critical section')
        a += 1
        print(f'{tid}-{i}: End of non-critical section')

        print(f'{tid}-{i}: Critical section')
        b_semaphore.acquire()
        try:
            v = common.value + 1
            common.value = v
        finally:
            b_semaphore.release()

        print(f'{tid}-{i}: End of critical section')

def main():
    lp = []
    common = Value('i', 0)          # "variable" en comun
    b_semaphore = BoundedSemaphore(1)

    for tid in range(N):
        lp.append(Process(target=task, args=(common, tid, b_semaphore)))
    print (f"Valor inicial del contador {common.value}")
    for p in lp:
        p.start()

    for p in lp:
        p.join()

    print (f"Valor final del contador {common.value}")
    print ("fin")

if __name__ == "__main__":
    main()