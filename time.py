import time


def get_sec_as_hms(duration: float) -> tuple:
    """
    Convert seconds to hours, minutes, seconds.

    Args:
        duration: Time duration in seconds

    Returns:
        tuple: (hours, minutes, seconds)
    """
    hours   = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = (duration % 3600) % 60

    return hours, minutes, seconds



def print_status_with_time(i, i_max, start_time):
    """
    Print status with elapsed time in formatted output.

    Args:
        i: Current iteration number
        i_max: Maximum number of iterations
        start_time: Start time of process

    Raises:
        ValueError: If i or i_max are negative, or if i_max is zero
    """
    if i<0 or i_max<0:
        raise ValueError("Only positive numbers of current entry and total number of entries are allowed!")

    if i_max==0:
        raise ValueError("Total number of entries shouldn't be zero!")


    elapsed_time = time.time() - start_time
    percent = i*100/i_max

    h, m, s = get_sec_as_hms(elapsed_time)

    out1 = "\r\033[1;31m >>"
    out2 = f"{out1} \033[1;32m [".rjust(5) + f"{percent:.02f}".zfill(5) + "%]\033[0m".ljust(13)
    out3 = f"{i+1:,}/{i_max:,}".ljust(25)
    out4 = "\033[1;34m" + f"{h:02d}:{m:02d}:{round(s):02d}\033[0m"
    out5 = " (hh:mm:ss)"
    out  = out1 + out2 + out3 + out4 + out5

    if i+1 != i_max: print(out,        flush=True, end=" ")
    else:           print(f"{out}\n", flush=True, end="\n")

def print_status(i, i_max, start_time: float, count: int = 0) -> int:
    """
    Print periodic status updates.

    Args:
        i: Current iteration number
        i_max: Maximum number of iterations
        start_time: Start time of process
        count: Counter for controlling update frequency

    Returns:
        int: Updated count value
    """
    if (time.time() - start_time > count):
        print_status_with_time(i, i_max, start_time)
        count += 1
    elif (i == i_max-1):
        print_status_with_time(i, i_max, start_time)

    return count
