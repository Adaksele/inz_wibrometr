#
# plik zawierający metody do zarządzania plikami
# https://stackoverflow.com/questions/17984809/how-do-i-create-an-incrementing-filename-in-python
#
#
#
import os
import queue

def next_path(path_pattern):
    """
    Finds the next free path in an sequentially named list of files

    e.g. path_pattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1

    # First do an exponential search
    while os.path.exists(path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b
    
def save_to_file(file_name, data_queue):
    try:
        file = open(f"{file_name}.csv", "w")
        file.write("t,\t X,\t Y,\t Z\t\n")
        size_of_queue = data_queue.qsize()
        print(size_of_queue)
        while data_queue.qsize() > 0:
            test = data_queue.get_nowait()
            print(test)
            file.write(f"{test}\n")
        #file.write(f"\n")
        file.close()
    except Exception:
        return 0
    finally:
        return 1

def save_to_file_increment(file_name, data_queue):
    pass
    new_file = next_path(file_name + "-%s.csv")
    file = open(f"{new_file}", "w")
    for row in data_queue:
        print(row)
        #file.write(row.)
    #file.close()
    try:
        pass
    except Exception:
        return 0
    finally:
        file.close()
        print("plik utworzony")
        return 1

if __name__ == "__name__":
    data_list = [[0, 0, 2, 0, 254, 254],
    [0, 0, 2, 0, 248, 254],
    [252, 255, 6, 0, 244, 254],
    [0, 0, 4, 0, 246, 254],
    [0, 0, 2, 0, 250, 254]]

    q = queue.Queue()
    for element in data_list:
        q.put_nowait(element)
        #print(element)

    #size = q.qsize()
    #print(size)
    name = "t0"
    save_to_file(name, q)
    #while q.qsize() > 0:
#    print(f"q size= {q.qsize()},\t oldest q = {q.get_nowait()}")