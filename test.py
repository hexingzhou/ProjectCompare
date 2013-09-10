import threading

class URLList():
    """
    docstring for URLList
    """
    def __init__(self, threading_lock):
        self._threading_lock = threading_lock
        self._exit_flag = False
        self._list = []
        self._append_count = 0
        self._pop_count = 0

    def pop(self):
        self._threading_lock.acquire()
        if len(self._list) > 0:
            url = self._list.pop()
            print '[pop]', url
            self._pop_count += 1
        self._threading_lock.release()

    def append(self, obj):
        self._threading_lock.acquire()
        print '[append]', obj
        self._list.append(obj)
        self._append_count += 1
        self._threading_lock.release()



class AppendThread(threading.Thread):
    """
    docstring for AppendThread
    """
    def __init__(self, thread_id, count, url_list):
        super(AppendThread, self).__init__()
        self._thread_id = thread_id
        self._count = count
        self._url_list = url_list

    def run(self):
        while self._count:
            url = 'thread_id: ' + str(self._thread_id) + ' count: ' + str(self._count)
            self._url_list.append(url)
            self._count -= 1


class PopThread(threading.Thread):
    """
    docstring for PopThread
    """
    def __init__(self, thread_id, url_list):
        super(PopThread, self).__init__()
        self._thread_id = thread_id
        self._url_list = url_list

    def run(self):
        while True:
            self._url_list.pop()


def _test():
    """
    a test function
    """
    thread_lock = threading.Lock()
    url_list = URLList(thread_lock)

    at1 = AppendThread(1, 10, url_list)
    at2 = AppendThread(2, 20, url_list)
    pt = PopThread(3, url_list)

    pt.start()
    at1.start()
    at2.start()

if __name__ == '__main__':
    _test()