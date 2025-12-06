"""
title: server/client 2.7 project
author: Yves Alon Numa
date: 4.12.2025
description: this is the server code
to the server the client connecting and sends him the commands:
dir,copy,execute,delete,take_screenshot and send_photo
until the command exit that disconnect this user from the server and the server can handle other client
"""
import logging
import socket
import glob
import os
import subprocess
import pyautogui
import shutil


def main():
    """
    Main function for the server that the client will use and sent exit/dir/copy/execute/delete/take_screenshot/send_photo commands to
    """
    global output
    READ_LEN = 1
    QUEUE_LENGTH = 1
    PORT = 8820
    IP = '0.0.0.0'
    while True:
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            my_socket.bind((IP, PORT))
            my_socket.listen(QUEUE_LENGTH)
            client_socket, client_address = my_socket.accept()
            try:
                while True:
                        client_info = recv_with_protocol(client_socket, READ_LEN)
                        cmd = client_info[0]
                        data = client_info[1]
                        if cmd == "DIR":
                            output = dir(data)
                        elif cmd == "DELETE":
                            output = delete(data)
                        elif cmd == "COPY":
                            output = copy(data)
                        elif cmd == "EXECUTE":
                            output = execute(data)
                        elif cmd == "TAKE_SCREENSHOT":
                            output = take_screenshot()
                        elif cmd == "SEND_PHOTO":
                            output = send_photo()
                        elif cmd == "EXIT":
                            output = "the server disconnected the client"
                        sent_with_protocol(client_socket, output, cmd)
                        if cmd == "EXIT":
                            break
            except socket.error as err:
                logging.info("Server Received Error"+str(err))
        except socket.error as err:
            logging.info("Server Received Error "+str(err))


def sent_with_protocol(client_socket, output, cmd):
    '''
    the fanction that sends the output of the wanted command to the server with protocol
    :param client_socket:
    :param output:
    :param cmd:
    :return: send to the client the desired output of the wanted command
    '''
    try:
        output_len = str(len(output))
        if cmd != "SEND_PHOTO":
            client_socket.send((output_len + "|" + output).encode())
            if cmd == "EXIT":
                client_socket.close()
        else:
            client_socket.send((output_len + "|").encode() + output)
        return
    except socket.error as err:
        output = "received error:" + str(err)
        output_len = str(len(output))
        client_socket.send((output_len + "|" + output).encode())
        logging.info("Server didn't send any data")
        return


def recv_with_protocol(client_socket, READ_LEN):
    '''
    the fanction that receives the output of the wanted command and his data from the client with protocol
    :param client_socket:
    :param READ_LEN:
    :return: the client info, the wanted command and the data of the wanted command
    '''
    try:
        cmd_len = ""
        while True:
            next_char = client_socket.recv(READ_LEN).decode()
            if next_char == "|":
                break
            cmd_len += next_char
        cmd_len = int(cmd_len)
        cmd = client_socket.recv(cmd_len).decode()
        data_len = ""
        while True:
            next_char = client_socket.recv(READ_LEN).decode()
            if next_char == "|":
                break
            data_len += next_char
        data_len = int(data_len)
        if data_len != 0:
            data = client_socket.recv(data_len).decode()
        else:
            data = ""
        client_info = [cmd, data]
        return client_info
    except socket.error as err:
        return "socket error: str(err)"
        logging.info("Server Received Error2")


def dir(data):
    '''
    the fanction that receives path and retutn the files in the directory of the wanted path
    :param data:
    :return: the wanted files from the wanted directory or message if the command failed
    '''
    try:
        if data != '*':
            data+='/*'
        contents = glob.glob(data)
        str_files = ""
        for item in contents:
            item = item.split('\\')
            item = item[len(item) - 1]
            str_files += str(item) + "\n"
        logging.info("dir succeeded and found the files:"+str(str_files))
        return str_files
    except Exception as e:
        logging.error(f"dir failed: {e}")
        return "DIR failed "+ str(e)


def delete(data):
    '''
    the fanction that receives path and delete the files in the directory of the wanted path
    :param data:
    :return: delete the wanted files from the wanted directory or message if the command failed
    '''
    try:
        os.remove(data)
        logging.info(f"DELETE: {data}")
        return "DELETE succeeded"
    except Exception as e:
        logging.error(f"DELETE failed: {e}")
        return "DELETE failed"


def copy(data):
    '''
    the fanction that receives paths and copy the file from one directory to the other
    :param data:
    :return: copy the wanted file from one directory to the other or message if the command failed
    '''
    source = data.split('|')[0]
    destination = data.split('|')[1]
    try:
        shutil.copy(source, destination)
        logging.info(f"COPY: {source} → {destination}")
        return "COPY succeeded"
    except Exception as e:
        logging.error(f"COPY failed: {e}")
        return "COPY failed"


def execute(data):
    '''
    the fanction that receives path (application) and open it
    :param data:
    :return: open the application or message if the command failed
    '''
    try:
        subprocess.call(data)
        logging.info(f"EXECUTE: {data}")
        return "EXECUTE succeeded"
    except Exception as e:
        logging.error(f"EXECUTE failed: {e}")
        return "EXECUTE failed"


def take_screenshot():
    '''
    fanction that takes the screenshot
    :return: message if the command failed or succeed
    '''
    try:
        pyautogui.screenshot().save("screen.jpg")
        logging.info("Screenshot taken")
        return "SCREENSHOT succeeded"
    except Exception as e:
        logging.error(f"Screenshot failed: {e}")
        return "SCREENSHOT failed"


def send_photo():
    '''
    fanction that sends the photo to the client
    :return: message if the command failed or succeed
    '''
    try:
        with open("screen.jpg", "rb") as f:
            screenshot_data = f.read()
        logging.info(f"Screenshot ready: {len(screenshot_data)} bytes")
        return screenshot_data
    except Exception as e:
        logging.error(f"Send screenshot failed: {e}")
        return "SEND SCREENSHOT failed"


if __name__ == "__main__":
    logging.basicConfig(filename="server.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    assert dir("*") is not None, "assert test failed"
    assert delete("non_existing_file.txt") == "DELETE failed", "assert test failed"
    assert copy("non_existing_source.txt|destination.txt") == "COPY failed", "assert test failed"
    assert execute("non_existing_app.exe") == "EXECUTE failed", "assert test failed"
    assert take_screenshot() in ["SCREENSHOT succeeded", "SCREENSHOT failed"], "assert test failed"
    assert isinstance(send_photo(), bytes) or send_photo() == "SEND SCREENSHOT failed", "assert test failed"
    assert recv_with_protocol is not None, "assert test failed"
    assert sent_with_protocol is not None, "assert test failed"
    logging.info("all the asserts passed")
    main()
# protocol cmd_len+|+cmd+cmd_data_len+|data
# if cmd==copi so after data_len will have the length of both copies (separate by |)
# if cmd==take_screenshot data_len has to be 0