import socket

from app import config

class SingleInstanceException(BaseException):
    """当应用的另一个实例已在运行时抛出此异常。"""
    pass

class SingleInstance:
    """
    通过绑定一个本地TCP端口，确保只有一个应用实例在运行。

    如果端口已被占用，则假定另一个实例正在运行，并抛出
    SingleInstanceException。

    当对象被垃圾回收或进程退出时，套接字会自动关闭。
    """
    def __init__(self, app_name=config.APP_NAME):
        self.lock_socket = None
        # 根据应用名称生成一个唯一的端口号
        port_num = 50000 + sum(ord(c) for c in app_name) % 15000
        self.host = "127.0.0.1"
        self.port = port_num

        try:
            self.lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lock_socket.bind((self.host, self.port))
        except socket.error:
            self.lock_socket = None
            raise SingleInstanceException()

    def __del__(self):
        """通过关闭套接字来释放锁。"""
        if self.lock_socket:
            self.lock_socket.close()
