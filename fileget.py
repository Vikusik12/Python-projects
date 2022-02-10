# #
# # IPK2021 project 1
# # Author: Viktoryia Tomason (xtomas34)
# #
import socket
import sys
import re

encoding = 'utf-8'
tcp_port = tcp_ip = for_tcp = 0
port = ip_ad = answer  = k = lent =  0
folder = filep = strok= stro = bytess =  kek = ""

reg = '^[\w\-\.]+$'
regn = '^[\d]+$'
human_found = False


if len (sys.argv) !=5:
    print ("ERROR")
    sys.exit(1)
else: 
    param_n = sys.argv[1]
    param_f = sys.argv[3]
    if (param_n == "-n" and param_f == "-f"):
        human_found = False
    elif (param_n == "-f" and param_f == "-n"):
        human_found = True
    else:
        sys.exit(1)

def check_arg(argv_2, argv_4):
    ip_ad = argv_2.split(':')[0]
    port = argv_2.split(':')[1]

    if re.match(regn,port) is None:#check server name
        print("Invalid port")
        exit(1)
    try:
        socket.inet_aton(ip_ad)
    except socket.error:
        print("Invalid IP")
        exit(1)
    order = argv_4.split("//")[1]
    kek =  argv_4.split("//")[0]
    if kek != 'fsp:':
        exit('Invalid protocol')
    folder = order.split("/",1)
    if re.match(reg,folder[0]) is None:#check server name
        exit(1)
    filep = order.split("/")[1]
    return ip_ad, port, folder[0], filep


def socket_udp(ip_ad,folder, port):
    sen = None
    mes_udp = f'WHEREIS {folder}\r\n\r\n'
    for res in socket.getaddrinfo(ip_ad, port, socket.AF_UNSPEC, socket.SOCK_DGRAM):
        ello, type_of_sock, value, canonname, ptr = res
        try:
            sen = socket.socket(ello, type_of_sock, value)
        except ConnectionRefusedError as mes_udp:
            sen = None
            continue
        try:
            sen.connect(ptr)
        except ConnectionRefusedError as mes_udp:
            sen.close()
            sen = None
            continue
        break
    if sen is None:
        print('Can not open it')
        sys.exit(1)

    with sen:
        sen.sendall(mes_udp.encode(encoding))
        try:
            data = sen.recv(1024)
        except OSError:
            exit('Disconnecting the connection')
        sen.close()   
    answer = (data.decode(encoding)).split(' ')
    if answer[0] == 'OK':
        for_tcp = answer[1].split(':')
        tcp_ip = for_tcp[0]
        tcp_port = for_tcp[1]
        return tcp_ip, int(tcp_port)
    else:
        exit('Disconnecting the connection')

def socket_tcp(ip_ad,filep,folder, port):
    soc = None
    if (filep == '*'):
        mes_tcp = f'GET index FSP/1.0\r\nHostname:{folder}\r\nAgent:xtomas34\r\n\r\n'
    else:
        mes_tcp = f'GET {filep} FSP/1.0\r\nHostname:{folder}\r\nAgent:xtomas34\r\n\r\n'

        if filep == '':
            exit(0)

    for res in socket.getaddrinfo(ip_ad, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        ello, type_of_sock, value, canonname, ptr = res
        try:
            soc = socket.socket(ello, type_of_sock, value)
        except ConnectionRefusedError as mes_tcp:
            soc = None
            continue
        try:
            soc.connect(ptr)
        except ConnectionRefusedError as mes_tcp:
            soc.close()
            soc = None
            continue
        break
    
    if soc is None:
        print('Can not open it')
        sys.exit(1)
    strok = b''
    with soc:
        soc.sendall(mes_tcp.encode(encoding,errors="ignore"))
        while 1:
            data = soc.recv(1024)
            if not data:
                break
            strok +=data
        bytess = strok.split(b'\r\n\r\n',1)
        if (bytess[0].split(b' '))[1][:7]!= b'Success':
            exit(bytess[1].decode())

        filep = filep.split('/')[-1]
        f = open(filep, "wb")
        if filep == "*":
            human_found = True
            for line in bytess: 
                typess = line.split(b'\r\n')
            for filep in typess:
                socket_tcp(tcp_ip, filep.decode(), folder, tcp_port)
        f.write(bytess[1])
        f.close()


if (human_found):
    ip_ad, port, folder, filep = check_arg(sys.argv[4],sys.argv[2])
else:
    ip_ad, port, folder, filep = check_arg(sys.argv[2],sys.argv[4])

socket_udp(ip_ad,folder,port)
tcp_ip, tcp_port = socket_udp(ip_ad,folder,port)
socket_tcp(tcp_ip,filep,folder, tcp_port)
