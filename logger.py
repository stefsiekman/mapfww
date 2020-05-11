from time import strftime

file = None


def start():
    global file

    time = strftime("%Y%m%d_%H%m%S")
    file = open(f"logs/log_{time}.txt", "w")


def info(msg=None, end="\n"):
    # return
    file.write(str(msg))
    file.write(end)
    print(msg, end=end)
    file.flush()


def debug(msg=None, extra=None):
    return
    file.write(str(msg))
    if extra is not None:
        file.write(" ")
        file.write(str(extra))
    file.write("\n")
    file.flush()
