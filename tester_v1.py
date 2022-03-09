import requests
addr = "http://127.0.0.1:8000/345/"
good_test, bad_test, server_errors = 0, 0, 0


def send_req(req_type, cmd, data=None, testval=None):
    global good_test, bad_test, server_errors

    if req_type == "post":
        re = requests.post(addr+cmd, data=data.encode())
    else:
        re = requests.get(addr+cmd)

    if testval == None:
        passed = "[no test]"
    elif testval == re.text:
        passed = "[passed]"
        good_test += 1
    else:
        passed = f"[ERROR, expected: {testval}]"
        bad_test += 1

    if re.status_code != 200:
        server_errors += 1

    print(f"{passed} {cmd} {str(data)} {re} {re.text}")
    # requests.session().close()


print("")
print(f"==================> Begin tests:")

send_req("get", "delete/testvar1")
send_req("post", "set/testvar1", "test1")
send_req("get", "get/testvar1", None, "test1")
send_req("get", "delete/testvar1", None, "test1")
send_req("get", "get/testvar1", None, "")

print("")

send_req("get", "delete/testvar3")
send_req("post", "push/testvar3", "test2")
send_req("post", "push/testvar3", "test3")
send_req("post", "push/testvar3", "test4")
send_req("get", "get/testvar3")
send_req("get", "fifopop/testvar3", None, "test2")
send_req("get", "lifopop/testvar3", None, "test4")
send_req("get", "lifopop/testvar3", None, "test3")
send_req("get", "list/all")

print(
    f"===== TOTAL TEST RESULT: {good_test} passed, {bad_test} failed, {server_errors} errors from server")
