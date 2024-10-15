import socket
import ssl
import sys
import os
import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.handle_scroll)

    def handle_scroll(self, e):
        if e.delta < 0:
            self.scrolldown(e)
        else:
            self.scrollup(e)

    def scrolldown(self, e):
        max_h = self.display_list[-1][1]
        self.scroll = min(self.scroll + SCROLL_STEP, max_h - SCROLL_STEP)
        self.draw()

    def scrollup(self, e):
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()

    def load(self, url):
        body = url.request()
        text = ''
        if url.viewsource:
            text = body
        else:
            text = lex(body)
        self.display_list= layout(text)
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)

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

def lex(body):
    text = ""
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
                text += "<"
                increment = 4
            elif c == "&" and c2 == "g" and c3 == "t" and c4 == ";":
                text += ">"
                increment = 4
            else:
                text += c
        i += increment
    return text

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        if c == "\n":
            cursor_y += VSTEP
            cursor_x = HSTEP
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list

if __name__ == "__main__":
    import sys
    current_directory = os.path.dirname(os.path.abspath(__file__))
    default_url = f"file:///{os.path.join(current_directory, 'error.html')}"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    Browser().load(URL(url))
    tkinter.mainloop()
