'''
st-toolset.py

Version 0.2.1

Created 2021 Oct 09
Last edited 2021 Oct 10

'''

import socket
import getopt
import sys
import threading
import os

target = "0.0.0.0"
port = 8080
file_path = ""
client_mode = False
server_mode = False
file_mode = False
hostname = socket.gethostname()
self_ip = socket.gethostbyname(hostname)

CHUNKSIZE = 1024

info = """
USAGE INFO
----------
-s, --server = server mode*
-h, --help = usage
-v, --version = version
-c, --client = client mode*
-p, --port <PORT> = port (default=8080)
-t, --target <TARGET> = target host (default=0.0.0.0)*
-g, --getip = get ip address
-f, --file <PATH> = send a file
-c, --chunksize = chunk size (default=1024 byte)

* REQUIRED (client OR server mode)
** REQUIRED IN CLIENT MODE
----------
In client text mode type ":end" to end sending.
"""

versioninfo = """
Socket TCP Transmission Toolset
Version 0.2.1
"""

def usage():
    print(info)
    exit()

def version():
    print(versioninfo)
    exit()

def getip():
    print("Hostname: %s\nIP Address: %s ."%(hostname, self_ip))
    exit()

def client_startup(connection, fpath):
    if file_mode:
        permission_ask_str = ":permissionrequest_file"
    else:
        permission_ask_str = ":permissionrequest"
    quitting = False

    try:
        connection.connect((target, port))
        connection.send(permission_ask_str.encode())
        print("[*] Requet sent, awaiting permission from server...")
        permission_response = connection.recv(CHUNKSIZE*4)
    except:
        errstr = "[!] Connection error: error establishing connection."
        print(errstr)
        return

    if permission_response.decode() == ":permitted":
        print("[+] Connection accepted, ready to send data.")
    else:
        print("[-] Connection refused.")
        return        
    
    close_connection = False
    end_str = ":end"
    
    if file_mode:
        try:
            print("[+] Sending...")
            file_name_extracted = os.path.basename(file_path)
            connection.send(file_name_extracted.encode())
            
            fobj = open(fpath, "rb")
            file_data = fobj.read(CHUNKSIZE)
            
            while file_data:
                connection.send(file_data)
                file_data = fobj.read(CHUNKSIZE)

            fobj.close()
            connection.close()
            print("[+] Done.")
        except Exception as e:
            print(str(e))
            print("[!] Unable to send file.")
    else:
        while True:
            message = input("> ")
            if message != ":end":
                try:
                    connection.send(message.encode())
                except:
                    print("[!] Failed to send message.")
                    break
            else:            
                connection.send(end_str.encode())
                close_connection = True
                break

    if close_connection:
        connection.send(":".encode())
        print("[+] Data sent, awaiting response from server...")
        response = connection.recv(CHUNKSIZE*4)
        print(response.decode())
        return


def server_startup(connection):
    def reprint():
        print("[*] Continue listening on %s:%d" % (target, port))

    def handle_client(client_socket, file_wanted):
        if file_wanted:
            file_basename = client_socket.recv(CHUNKSIZE).decode()
            print("[+] Receiving %s..."%file_basename)

            fobj = open(file_basename, "wb")
            file_chunk = client_socket.recv(CHUNKSIZE)

            while file_chunk:
                fobj.write(file_chunk)
                file_chunk = client_socket.recv(CHUNKSIZE)

            fobj.close()
            client_socket.close()

            print("[+] Receiving done, data saved to ./%s ."%file_basename)
            
            reprint()
            return

        else:
            print("<start of text>")
            while True:
                received_data_raw = client_socket.recv(CHUNKSIZE)
                received_data = recieved_data_raw.decode()
                if received_data != ":end":
                    print(received_data)
                else:
                    print("<end of text>")
                    data_exchange = "[SERVER,+] Data received."
                    client_socket.send(data_exchange.encode())
                    client_socket.close()
                    reprint()
                    return
    
    try:
        connection.bind((target, port))
        connection.listen(5)
        infostr = "[+] Server created. Listening on %s:%d ." % (target, port)
        print(infostr)
    except:
        print("[!] Error creating server.")

    block_list = []

    while True:
        client,addr = connection.accept()

        file_wanted = False

        if addr[0] not in block_list:
            check_in_attempt = client.recv(CHUNKSIZE).decode()
            if check_in_attempt in (":permissionrequest", ":permissionrequest_file"):
                if check_in_attempt == ":permissionrequest":
                    user_response = input("[*] Incoming connection request from %s. Accept? [y/n] "%addr[0])
                else:
                    user_response = input("[*] Incoming connection request (filemode) from %s. Accept? [y/n]"%
                        addr[0])
                    file_wanted = True

                if user_response in ("y","yes","Y", "YES"):
                    permitted_str = ":permitted"
                    client.send(permitted_str.encode())
                    print("[+] Established connection with client. Recieving...")
                    client_handler = threading.Thread(target=handle_client, args=(client,file_wanted,))
                    client_handler.start()
                    file_wanted = False
                else:
                    refused_str = ":refused"
                    client.send(refused_str.encode())
                    refused_block = input("[*] Connection refused. Block this IP? [y/n] ")
                    file_wanted = False
                    if refused_block in ("y","yes","Y","YES"):
                        block_list.append(addr[0])
                    reprint()
            else:
                print("[!] Unrecognized check-in ID. Connection closed for security.")
                reprint()

def main():
    global port
    global target
    global client_mode
    global server_mode
    global file_mode
    global file_path
    global CHUNKSIZE

    fobj_tmp = None

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsvgct:p:f:c:", 
                ["help", "client", "target=", "port=", "version", "server", 
                 "getip", "file=", "chunksize="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-c", "--client"):
            client_mode = True
        elif o in ("-f", "--file"):
            file_mode = True
            file_path = a
            print("[*] Entering file mode.")
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            try:
                port = int(a)
            except:
                print("[!] <PORT> must be an integer.")
                usage()
        elif o in ("-v", "--version"):
            version()
        elif o in ("-s", "--server"):
            server_mode = True
        elif o in ("-g", "--getip"):
            getip()
        elif o in ("-c", "--chunksize"):
            CHUNKSIZE = int(a)

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if file_mode:
        if not client_mode:
            print("[!] --file can only be selected in client mode.")
            usage()
        else:
            try:
                fobj_tmp = open(file_path, "rb")
            except:
                print("[!] File does not exist or corrupted.")
    if client_mode and target != "0.0.0.0":
        client_startup(connection, file_path)
    elif server_mode:
        server_startup(connection)
    else:
        print(client_mode, server_mode, target, port)
        assert False, "[!] Invalid options."

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Script aborted: KeyboardInterrupt.")
