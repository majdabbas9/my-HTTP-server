import socket  # noqa: F401
import os
import re

def read_file(file):
    with open(file, "r") as f:
        content = f.read()
    return content

def clean_math_expression(text):
    # Keep only digits, operators (+, -, *, /, %), spaces, and parentheses
    cleaned = re.sub(r'[^0-9+\-*/%().\s]', '', text)
    return cleaned.strip()

def safe_eval(expression):
    cleaned = clean_math_expression(expression)
    try:
        result = eval(cleaned)
        return result
    except Exception as e:
        return f"Error: {e}"
    
def GET_hanler(URL_PATH,URL,BASE_DIR):
    if URL_PATH == "":
        return "HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
    elif URL_PATH.startswith("echo/") :
        str1 = URL_PATH.split("/")[1]
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(str1)}\r\n\r\n{str1}"
    elif URL_PATH == "user-agent":
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(URL[2].split()[1])}\r\n\r\n{URL[2].split()[1]}"
    elif ".html" in URL_PATH:
        file_content = read_file(URL_PATH)
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(file_content)}\r\n\r\n{file_content}"

    elif URL_PATH.startswith("files"):
        file = URL_PATH.split("/")[1]
        file_path = os.path.join(BASE_DIR,file)
        if os.path.isfile(file_path):
            file_content = read_file(file)
            return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_content)}\r\n\r\n{file_content}"
        else :
            print(f"file {file} is not found")
            return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    else:
        return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
def POST_handler(URL_PATH,URL,REQ_body,BASE_DIR):
    if URL_PATH.lower() in ["calculator","calc","eval"]:
        res = safe_eval(REQ_body)
        body = str(res).encode("utf-8")
        return f"HTTP/1.1 201 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{res}".encode("utf-8")


def main():
    # Define socket host and port
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 4221

    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(1)
    print('Listening on port %s ...' % SERVER_PORT)
    while True:
        conn,adrr = server_socket.accept() # wait for client
        URL = conn.recv(1024).decode().split("\r\n")
        BASE_DIR = os.getcwd()
        if "GET" in URL[0]:
            URL_PATH = URL[0].split()[1][1:]
            conn.sendall(GET_hanler(URL_PATH,URL,BASE_DIR).encode())
        if "POST" in URL[0]:
            print(URL)
            URL_PATH = URL[0].split()[1][1:]
            conn.sendall(POST_handler(URL_PATH,URL,URL[-1],BASE_DIR))
        conn.close()
    server_socket.close()


if __name__ == "__main__":
    main()
