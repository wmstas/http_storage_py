import time
import sys
import requests

addr = "http://127.0.0.1:8000/345/"
good_test, bad_test, server_errors = 0, 0, 0
hide_ok_result = True


def send_req(cmd, data=None, testval=None):
    global good_test, bad_test, server_errors, hide_ok_result

    # ======> send request
    if cmd[:3] == "set" or cmd[:4] == "push":
        re = requests.post(addr+cmd, data=data.encode())
    else:
        re = requests.get(addr+cmd)

    # ======> check answer
    if testval == None and re.status_code == 200:
        good_test += 1
        if hide_ok_result:
            return
        passed = "[no test]"
    elif re.status_code != 200:
        passed = "[SERVER ERROR]"
        server_errors += 1
    elif testval == re.text:
        good_test += 1
        if hide_ok_result:
            return
        passed = "[passed]"
    else:
        passed = f"[ERROR, expected: {testval}]"
        bad_test += 1

    # ======> show errors (or may be OK result too)
    print(f"{passed} {cmd} {str(data)} {re} {re.text}")


def do_all_tests():
    send_req("delete/testvar1")
    send_req("set/testvar1", "test1")
    send_req("get/testvar1", None, "test1")
    send_req("delete/testvar1", None, "test1")
    send_req("get/testvar1", None, "")

    send_req("delete/testvar3")
    send_req("push/testvar3", "test2")
    send_req("push/testvar3", "test3")
    send_req("push/testvar3", "test4")
    send_req("get/testvar3")
    send_req("fifopop/testvar3", None, "test2")
    send_req("lifopop/testvar3", None, "test4")
    send_req("lifopop/testvar3", None, "test3")
    send_req("list/all")


# ====================================================================
if __name__ == "__main__":

    # ======> get argument from command line for time ([0] is module name, [1] arg1)
    if len(sys.argv) > 1:
        time_to_repeat = int(sys.argv[1])
    else:
        time_to_repeat = 0.001


print("")
print(f"==================> Begin tests:")

# ======> main cycle for running tests
time_start = time.time()
while time.time() - time_start < time_to_repeat:
    do_all_tests()

# ======> show total results
print(
    f"===== TOTAL TEST RESULT: {good_test} passed, {bad_test} failed, {server_errors} server errors")
time_end = time.time()
print(f"Duralition time: {time_end - time_start}")
