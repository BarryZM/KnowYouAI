from threading import Thread
from queue import Queue
import time
from _global import global_logger
# from core.constant import _ResponseType
import traceback
import config


class ThreadPool:
    def __init__(self):
        self.pool_size = config.THREADING_POOL_SIZE
        self.mission_queue = Queue()

        self.info_queue = Queue()  # 后台消息，若不调用callback则全部放进去缓存起来
        self._pool = [Thread(target=self._run) for _ in range(self.pool_size)]
        for i in range(len(self._pool)):
            self._pool[i].setDaemon(True)
            self._pool[i].start()
        self.running_mission_number = 0
        self.running_mission_name = {}
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def add_mission(self, mission):
        self.mission_queue.put(mission)

    def _run(self):
        while True:
            # 启动后就等待新任务
            mission = self.mission_queue.get()  # 阻塞
            name = mission.name
            if name in self.running_mission_name:
                name += "_{}".format(int(time.time()))
            self.running_mission_name[name] = 1
            self.running_mission_number += 1
            try:
                mission.run()
                del self.running_mission_name[name]
            except Exception:
                info = traceback.format_exc()
                if config.INFO_ACKNOWLEDGE and self.callback is not None:
                    self.callback(info)
                else:
                    self.info_queue.put(info)
                global_logger.info("任务{name}出问题了。问题报告:{info}".format(name=name, info=info))
            self.running_mission_number -= 1
