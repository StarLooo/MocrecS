class Circular_Queue(object):

    def __init__(self, size):
        self.size = size  # 定义队列长度
        self.queue = []  # 用列表来模拟队列

    def __str__(self):
        # 返回对象的字符串表达式，方便查看
        return str(self.queue)

    # 入队，如果队列已满，则先删除对头元素再入队
    def enQueue(self, new_ele):
        if self.isFull():
            self.deQueue()
        self.queue.append(new_ele)

    # 出队，仅在enQueue中调用，其余情况请勿手动调用
    def deQueue(self):
        head_ele = None
        flag = False
        if not self.isEmpty():
            flag = True
            head_ele = self.queue[0]  # 删除队头元素
            self.queue.remove(head_ele)  # 删除队操作
        # return head_ele, flag

    def isEmpty(self):
        if len(self.queue) == 0:
            return True
        return False

    def isFull(self):
        if len(self.queue) == self.size:
            return True
        return False

    # 一些其它不需要的方法
    # def delete_pos(self, n):
    #     element = self.queue[n]
    #     self.queue.remove(element)
    #
    # def input(self, n, m):
    #     # 插入某元素 n代表列表当前的第n位元素 m代表传入的值
    #     self.queue[n] = m
    #
    # def get_size(self):
    #     # 获取当前长度
    #     return len(self.queue)
    #
    # def get_number(self, n):
    #     # 获取某个元素
    #     element = self.queue[n]
    #     return element


# 测试
if __name__ == '__main__':
    cq = Circular_Queue(5)  # 定义一个大小为5的队列
    for i in range(8):
        cq.enQueue(i)
        print(cq)
