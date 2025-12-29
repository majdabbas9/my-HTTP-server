import socket
import os
import re

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=4221):
        self.host = host
        self.port = port
        self.base_dir = os.getcwd()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    def _read_file(self, file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return content

    @staticmethod
    def _clean_math_expression(text):
        # Keep only digits, operators (+, -, *, /, %), spaces, and parentheses
        cleaned = re.sub(r'[^0-9+\-*/%().\s]', '', text)
        return cleaned.strip()

    def _safe_eval(self, expression):
        cleaned = self._clean_math_expression(expression)
        try:
            result = eval(cleaned)
            return result
        except Exception as e:
            return f"Error: {e}"

    def handle_get_request(self, url_path, url_parts):
        if url_path == "":
            return "HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
        elif url_path.startswith("echo/"):
            # Original code: str1 = URL_PATH.split("/")[1]
            # url_path is already the part after GET /... but logic in original was:
            # URL_PATH = URL[0].split()[1][1:] -> which is "echo/hello"
            # So splitting by "/" works.
            str1 = url_path.split("/")[1]
            return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(str1)}\r\n\r\n{str1}"
        elif url_path == "user-agent":
            # url_parts is the full list from split("\r\n").
            # URL[2] in original code (index 2) usually contains User-Agent if formatted standardly,
            # but let's stick to the original logic which relied on fixed index.
            # Original: URL[2].split()[1]
            user_agent_line = url_parts[2]
            user_agent = user_agent_line.split()[1]
            return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
        elif ".html" in url_path:
            file_content = self._read_file(url_path)
            return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(file_content)}\r\n\r\n{file_content}"
        elif url_path.startswith("files"):
            file_name = url_path.split("/")[1]
            file_path = os.path.join(self.base_dir, file_name)
            if os.path.isfile(file_path):
                file_content = self._read_file(file_name)
                return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_content)}\r\n\r\n{file_content}"
            else:
                print(f"file {file_name} is not found")
                return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
        else:
            return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

    def handle_post_request(self, url_path, url_parts, req_body):
        if url_path.lower() in ["calculator", "calc", "eval"]:
            res = self._safe_eval(req_body)
            body = str(res).encode("utf-8")
            return f"HTTP/1.1 201 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{res}".encode("utf-8")
        return b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

    def start(self):
        self.server_socket.listen(1)
        print(f'Listening on port {self.port} ...')
        try:
            while True:
                conn, addr = self.server_socket.accept()  # wait for client
                try:
                    # Read headers
                    request_data = b""
                    while b"\r\n\r\n" not in request_data:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        request_data += chunk
                    
                    if not request_data:
                        conn.close()
                        continue

                    header_part, body_part = request_data.split(b"\r\n\r\n", 1)
                    headers_str = header_part.decode()
                    url_parts = headers_str.split("\r\n")
                    
                    request_line = url_parts[0]
                    parts = request_line.split()
                    if len(parts) < 2:
                        conn.close()
                        continue
                        
                    method = parts[0]
                    path = parts[1][1:]
                    req_body = body_part.decode()
                    print(req_body)
                    # Handle Content-Length for POST
                    content_length = 0
                    if "POST" in method:
                        for line in url_parts[1:]:
                            if line.lower().startswith("content-length:"):
                                try:
                                    content_length = int(line.split(":")[1].strip())
                                except ValueError:
                                    pass
                        
                        while len(req_body.encode()) < content_length:
                            chunk = conn.recv(1024)
                            if not chunk:
                                break
                            req_body += chunk.decode()

                    response = None
                    if "GET" in method:
                        response = self.handle_get_request(path, url_parts).encode()
                    elif "POST" in method:
                        response = self.handle_post_request(path, url_parts, req_body)
                    
                    if response:
                        conn.sendall(response)
                        
                except Exception as e:
                    print(f"Error handling request: {e}")
                finally:
                    conn.close()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = HTTPServer(port=8000)
    server.start()
