from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

token = "345"
dbf = {}
show_log = False


def cmd_push(varname, value):
    data = dbf.get(varname, [])
    data.append(value)
    dbf[varname] = data
    return f"[ok] pushed into array {varname} <= {value}"


def cmd_set(varname, value):
    dbf[varname] = value
    return f"[ok] set var {varname} <= {value}"


def cmd_get(varname):
    data = dbf.get(varname, "")
    return data


def cmd_list():
    list_keys = list(dbf.keys())
    list_keys.sort()
    re = " ".join(list_keys)
    return re


def cmd_pop(varname, fifo=False):
    data = dbf.get(varname, [])
    if type(data) != list:
        raise Exception(f"requested value: {varname} is not array")
    if len(data) == 0:
        return ""
    else:
        if fifo:
            re = data.pop(0)
        else:
            re = data.pop()
        # no need for this line in DICT, but when it will be SQL - remember
        # dbf[varname] = data
        return re


def cmd_delete(varname):
    re = str(dbf.get(varname, ""))
    if varname in dbf.keys():
        del dbf[varname]
    return re


def get_data_from_request_path(path):
    m = path.lower().split("/")
    m = m[-3:]

    # ====== authorization test
    if len(m) < 3:
        return False, "", 400
    elif m[0] != token:
        return False, "", 401

    # ====== return data
    return True, m[1], m[2]


def send_http_answer(request, code, str_answer):
    request.send_response(code)
    request.send_header("Content-type", "text/html")
    request.end_headers()
    request_answer = str(str_answer).encode()
    request.wfile.write(request_answer)
    if show_log:
        print(f"   => "+str(str_answer))


class HttpGetHandler(BaseHTTPRequestHandler):
    """HTTP Server request handler class"""

    def log_message(self, format, *args):
        """Disable show logs on screen. You can delete this, for shown"""
        pass

    def do_GET(self):
        """get data from storage"""
        auth, cmd, varname = get_data_from_request_path(self.path)
        if auth == False:
            errorCode = varname
            send_http_answer(self, errorCode, "")
            return

        try:
            if cmd == "get":
                re = cmd_get(varname)
            elif cmd == "list":
                re = cmd_list()
            elif cmd == "lifopop":
                re = cmd_pop(varname, False)
            elif cmd == "fifopop":
                re = cmd_pop(varname, True)
            elif cmd == "delete":
                re = cmd_delete(varname)
            else:
                raise Exception(f"invalid command in your request: {cmd}")

        except BaseException as err:   # when some error, return it to user
            send_http_answer(self, 500, err)
            return

        send_http_answer(self, 200, re)

    def do_POST(self):
        """add new data to storage"""
        auth, cmd, varname = get_data_from_request_path(self.path)
        if auth == False:
            errorCode = varname
            send_http_answer(self, errorCode, "")
            return

        try:
            # ====== 1. get value from request
            content_length = int(self.headers.get(
                "Content-Length", "0"))  # get the size of data
            if content_length == 0:
                value = ""
            else:
                value_byte = self.rfile.read(
                    content_length)  # gets the data itself
                value = value_byte.decode()

            # ====== 2. get value from request
            if cmd == "push":
                re = cmd_push(varname, value)
            elif cmd == "set":
                re = cmd_set(varname, value)
            else:
                raise Exception("invalid command in your request: "+cmd)

        except BaseException as err:   # when some error, return it to user
            send_http_answer(self, 500, err)
            return

        send_http_answer(self, 200, re)


# =============== main
server_address = ("", 8000)
httpd = HTTPServer(server_address, HttpGetHandler)
try:
    print("+ Server started")
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.server_close()
    print("- Server closed")
