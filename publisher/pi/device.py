def get_device_id():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
        return cpuserial
    except:
        raise Exception('Exception: Could not find serial number')


if __name__ == "__main__":
    print(get_device_id())
