from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import FallbackHandler, RequestHandler, Application
from tornado.websocket import WebSocketHandler
from tornado import escape
import json
import time
import statistics

interval_ms = 0.01

start = time.time()

def watch():
    global start
    if len(MonitorSocket.waiters) > 0:
        # print(f'Time: {start - time.time()}|', end='')
        start = time.time()
        MonitorSocket.send_change()
    # while True:
    #     MonitorSocket.send_change()
    #     time.sleep(interval)

class MonitorSocket(WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 5

    def check_origin(self, origin):
        return True

    def open(self, data):
        print('Client : Connection Opened')
        # data = json.loads(data)

        # self.write_message(json.dumps(response_data))
        MonitorSocket.waiters.add(self)

    @classmethod
    def send_change(cls):
        # response_data = {
        #     'status': 'Update',
        #     'type': 'operation',
        #     'data': change
        # }
        # response_data = str(statistics.get_cpu_info())
        response_data = str(statistics.get_layout2_statistics())
        # print('Change Response is : ', response_data)
        if '"' in response_data:
            pass
        else:
            response_data.replace("'",'"')
        for waiter in cls.waiters:
            waiter.write_message(response_data)

    def on_message(self, message):
        print('Message recieved as '+message)
        self.write_message(json.dumps(str({'hi': 'there'})))

    def on_close(self):
        print('Client : Connection Closed')
        MonitorSocket.waiters.remove(self)

application = Application([
    (r"/MonitorSocket/(.*)", MonitorSocket)
    ], websocket_max_message_size=1024**2)

if __name__ == "__main__":
    application.listen(5665)
    # IOLoop.instance().start()
    main_loop = IOLoop.current()
    sched = PeriodicCallback(watch, interval_ms)
    #start your period timer
    try:
        sched.start()
        main_loop.start()
    except KeyboardInterrupt:
        sched.stop()
        main_loop.stop()
