from time import strftime

file = None
should_force_flush = False
should_info = False
should_debug = False


def start(info=True, debug=False, force_flush=False):
    global file, should_force_flush, should_debug, should_info

    should_force_flush = force_flush
    should_info = info
    should_debug = debug

    time = strftime("%Y%m%d_%H%M%S")
    file = open(f"logs/log_{time}.txt", "w")


def stop():
    global file
    file.close()


def info(msg=None, end="\n"):
    if not should_info:
        return

    file.write(str(msg))
    file.write(end)
    print(msg, end=end)

    if should_force_flush:
        file.flush()


def debug(msg=None, extra=None):
    if not should_debug:
        return

    file.write(str(msg))
    if extra is not None:
        file.write(" ")
        file.write(str(extra))
    file.write("\n")

    if should_force_flush:
        file.flush()
