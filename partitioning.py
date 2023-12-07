def partition(N, k, list = []):
    g_list = []

    if k == 1: 
        return [g_list + [*list, N]]
    
    for i in range(1,10): # 'i' is from 1 to 9
        r = N - i
        if r <= 0: break
        if r/(k-1) > 9: continue # Skipping calculation of impossible partitions
        g_list = g_list + partition(r, k-1, list + [i])
        # g_list.append(partition(r, k-1, list + [i]))
    
    return g_list

def remove_duplicates(list):
    i = 0
    while i < len(list):
        if len(list[i]) != len(set(list[i])):
            del list[i]
        i += 1
def main():
    result = partition(17, 3)
    remove_duplicates(result)
    print(result)

if __name__ == '__main__':
    main()