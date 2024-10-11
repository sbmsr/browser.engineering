import socket
import ssl
import sys
import os
import tkinter

WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

    def load(self, url):
        body = url.request()
        if url.viewsource:
            print(body)
        else:
            show(body)
        
        self.canvas.create_rectangle(10, 20, 400, 300)
        self.canvas.create_oval(100, 100, 150, 150)
        self.canvas.create_text(200, 150, text="Hi!")


class URL:
    def __init__(self, url):
        self.viewsource = False
        if url.startswith("view-source:"):
            self.viewsource = True
            url = url.replace("view-source:","")
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "data", "view-source"]
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        elif self.scheme == "data":
            self.dataContentType, self.data = url.split(",", 1)
            return
        if "/" not in url:
            url += "/"
        self.host, url = url.split("/", 1)
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        self.path = "/" + url
    
    def request(self):
        if self.scheme == "file":
            return readFile(self.path)
        elif self.scheme == "data":
            assert self.dataContentType in ["text/html"]
            return self.data

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        
        s.connect((self.host, self.port))

        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: close \r\n"
        request += "User-Agent: Seb's Browser \r\n"
        request += "\r\n"
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        
        content = response.read()
        s.close()

        return content

def readFile(path): 
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

def replaceEntities(body):
    replaced = body.replace("&lt;", "<").replace("&gt;",">")
    return replaced


def show(body):
    in_tag = False

    i = 0
    while i < len(body):
        c = body[i]
        c2 = body[i+1] if i+1 < len(body) else ""
        c3 = body[i+2] if i+2 < len(body) else ""
        c4 = body[i+3] if i+3 < len(body) else ""

        increment = 1

        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            if c == "&" and c2 == "l" and c3 == "t" and c4 == ";":
                print("<", end="")
                increment = 4
            elif c == "&" and c2 == "g" and c3 == "t" and c4 == ";":
                print(">", end="")
                increment = 4
            else:
                print(c, end="")        
        i += increment

if __name__ == "__main__":
    import sys
    current_directory = os.path.dirname(os.path.abspath(__file__))
    default_url = f"file:///{os.path.join(current_directory, 'error.html')}"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    Browser().load(URL(url))
    tkinter.mainloop()
