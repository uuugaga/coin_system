import time

def show_total_history(total):
    f = open('./log/record.txt', 'r')
    line = 'empty\n'
    for line in f:
        pass
    print(f'last    --> {line}', end="")
    f.close()

    localtime = time.localtime(time.time())
    f = open('./log/record.txt', 'a+')
    f.write(f'total: {total / 1000000:.3f}m, {localtime.tm_year}/{localtime.tm_mon}/{localtime.tm_mday} | {localtime.tm_hour}:{localtime.tm_min}:{localtime.tm_sec}')
    print(f'current --> {total / 1000000:.3f}m, {localtime.tm_year}/{localtime.tm_mon}/{localtime.tm_mday} | {localtime.tm_hour}:{localtime.tm_min}:{localtime.tm_sec}')
    f.write('\n')
    f.close()

def read_config():
    f = open('config.txt', 'r')
    setting = []
    for line in f:
        line = line.replace('\n', '')
        setting.append(int(line.split('=')[1]))
    return setting