import datetime
import traceback

def get_error_log():
    error_log = traceback.print_exc()
    return error_log

def save_error_log(log_filename, error_info):
    sys_time = datetime.datetime.now()

    error_info = str(sys_time + '\n' + get_error_log())

    with open(log_filename, 'w') as file:
        file.write(error_info + '\n')
    return "Log saved!"
