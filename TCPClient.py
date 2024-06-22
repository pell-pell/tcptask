import socket
import struct
import random
import time


def read_file(file_path):
    """读取文件内容"""
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path, data):
    """将数据写入文件"""
    with open(file_path, 'w') as file:
        file.write(data)


def send_data(client_socket, data, msg_type):
    """发送数据到服务器"""
    length = len(data)
    header = struct.pack('!HI', msg_type, length)  # 构建报文头，包含类型和数据长度
    client_socket.send(header + data)  # 发送报文头和数据


def main(server_ip, server_port, lmin, lmax):
    """主函数，处理客户端的逻辑"""
    file_path = 'ascii_file.txt'  # 输入文件路径
    reversed_file_path = 'reversed_ascii_file.txt'  # 输出文件路径

    data = read_file(file_path)  # 读取文件内容
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP套接字
    client_socket.connect((server_ip, server_port))  # 连接服务器

    block_sizes = []  # 存储每个块的大小
    total_bytes_sent = 0
    while total_bytes_sent < len(data):
        block_size = random.randint(lmin, lmax)  # 随机生成块大小
        if total_bytes_sent + block_size > len(data):
            block_size = len(data) - total_bytes_sent  # 确保最后一块大小不超过剩余数据长度
        block_sizes.append(block_size)  # 记录块大小
        total_bytes_sent += block_size  # 更新已发送的总字节数

    N = len(block_sizes)  # 总块数

    # 发送初始化报文
    init_msg = struct.pack('!HI', 1, N)
    client_socket.send(init_msg)

    response = client_socket.recv(1024)  # 接收服务器响应
    msg_type, = struct.unpack('!H', response[:2])  # 解包响应类型
    if msg_type != 2:
        print('初始化失败.')
        return

    reversed_data = []  # 存储反转后的数据块
    start_index = 0

    for block_index, block_size in enumerate(block_sizes, start=1):
        chunk = data[start_index:start_index + block_size].encode('ascii')  # 获取当前块数据
        send_data(client_socket, chunk, 3)  # 发送反转请求报文

        response = client_socket.recv(1024)  # 接收服务器响应
        msg_type, length = struct.unpack('!HI', response[:6])  # 解包响应类型和长度
        reversed_chunk = response[6:6 + length].decode('ascii')  # 获取反转后的数据块

        print(f'第{block_index}块: {reversed_chunk}')  # 打印反转后的数据块

        reversed_data.append(reversed_chunk)  # 记录反转后的数据块
        start_index += block_size  # 更新开始索引

        # 增加延迟，以便有时间启动多个客户端
        time.sleep(1)

    client_socket.close()

    reversed_text = ''.join(reversed_data)  # 拼接所有反转后的数据块
    write_file(reversed_file_path, reversed_text)
    print('反转数据已保存到', reversed_file_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='TCP Client for text reversal')
    parser.add_argument('server_ip', help='服务器的IP地址')
    parser.add_argument('server_port', type=int, help='服务器的端口号')
    parser.add_argument('lmin', type=int, help='数据块的最小长度')
    parser.add_argument('lmax', type=int, help='数据块的最大长度')

    args = parser.parse_args()
    main(args.server_ip, args.server_port, args.lmin, args.lmax)  # 调用主函数
