import socket
import struct
import select

def reverse_string(s):
    """反转字符串"""
    return s[::-1]

def handle_data(client_socket, data):
    """处理从客户端接收到的数据"""
    # 解析消息类型
    msg_type, = struct.unpack('!H', data[:2])

    if msg_type == 1:
        # Initialization 消息，解析 N
        N, = struct.unpack('!I', data[2:6])
        print(f'Received Initialization message: N={N}')
        client_socket.send(struct.pack('!H', 2))  # 发送 Agree 消息

    elif msg_type == 3:
        # Reverse 请求，解析 length 和 payload
        length, = struct.unpack('!I', data[2:6])
        payload = data[6:6 + length].decode('ascii')
        reversed_text = reverse_string(payload)  # 反转字符串
        reversed_data = reversed_text.encode('ascii')
        response = struct.pack('!HI', 4, len(reversed_data)) + reversed_data
        client_socket.send(response)  # 发送反转后的数据

def start_server():
    """启动服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 14000))  # 绑定到所有可用的接口
    server_socket.listen(5)
    server_socket.setblocking(False)  # 设置非阻塞模式
    print('服务器监听端口 14000...')

    # 使用 select 监控 socket
    inputs = [server_socket]
    outputs = []
    client_data = {}

    while True:
        # 使用 select 监控输入、输出和异常的 socket
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        for s in readable:
            if s is server_socket:
                # 处理新的客户端连接
                client_socket, addr = server_socket.accept()
                print('接受连接来自:', addr)
                client_socket.setblocking(False)
                inputs.append(client_socket)
                client_data[client_socket] = b""
            else:
                # 处理来自客户端的消息
                data = s.recv(1024)
                if data:
                    client_data[s] += data
                    # 如果收到的数据长度足够处理一个完整的消息
                    while len(client_data[s]) >= 6:
                        msg_type, = struct.unpack('!H', client_data[s][:2])
                        if msg_type == 1:
                            if len(client_data[s]) >= 6:
                                handle_data(s, client_data[s][:6])
                                client_data[s] = client_data[s][6:]
                        elif msg_type == 3:
                            if len(client_data[s]) >= 6:
                                length, = struct.unpack('!I', client_data[s][2:6])
                                if len(client_data[s]) >= 6 + length:
                                    handle_data(s, client_data[s][:6 + length])
                                    client_data[s] = client_data[s][6 + length:]
                else:
                    # 客户端关闭连接
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del client_data[s]

        for s in writable:
            pass

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del client_data[s]

if __name__ == '__main__':
    start_server()
