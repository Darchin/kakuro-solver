class Partitioner:
    def partition(N, k, list = []):
        g_list = []

        if k == 0:
            return g_list
        if k == 1: 
            if N <= 0: return g_list
            if N <= 9: return [[*list, N]]
            return g_list
        
        for i in range(1,10): # 'i' is from 1 to 9
            r = N - i
            if r <= 0: break
            if r/(k-1) > 9: continue # Skipping calculation of impossible partitions
            g_list = g_list + Partitioner.partition(r, k-1, list + [i])
        
        return g_list

    def remove_duplicates(list):
        partitions = list.copy()
        i = 0
        while i < len(partitions):
            if len(partitions[i]) != len(set(partitions[i])):
                partitions.pop(i)
            else:
                i += 1
        return partitions
    def getOrderedPartitions(N, k) -> list:
        return Partitioner.remove_duplicates(Partitioner.partition(N, k))
    def flatten(list):
        return [item for sublist in list for item in sublist]
    def generatePartitionMask(partition_list):
        partition_mask = [False] * 9
        flattened_partition_list = Partitioner.flatten(partition_list)
        for i in range(1,10):
            if i in flattened_partition_list:
                partition_mask[i-1] = True
        return partition_mask
# print(Partitioner.getOrderedPartitions(17,2))