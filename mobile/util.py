import heapq
import time
from typing import ItemsView


class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        while self.isEmpty():
            if not self.isEmpty():
                (priority, _, item) = heapq.heappop(self.heap)
                return item, priority
        (priority, _, item) = heapq.heappop(self.heap)
        return item, priority

    # 空队列超过一定的时间，则返回NONE
    def threshold_pop(self, threshold):
        start = time.time()
        while self.isEmpty():
            if time.time() > start + threshold:
                return 'timeout'
            if not self.isEmpty():
                (priority, _, item) = heapq.heappop(self.heap)
                return item, priority
        (priority, _, item) = heapq.heappop(self.heap)
        return item, priority

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)
