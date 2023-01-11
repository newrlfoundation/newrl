import time
import requests

from requests.adapters import HTTPAdapter, Retry

from app.config.constants import TIME_DIFF_WITH_GLOBAL_FILE


def get_global_epoch():
    # url = 'http://worldclockapi.com/api/json/utc/now'
    url = 'https://worldtimeapi.org/api/timezone/Etc/UTC'
    s = requests.Session()

    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))

    # s.get('https://worldtimeapi.org/api/timezone/Etc/UTC')

    time_json = s.get(url).json()
    epoch = time_json['unixtime']
    return epoch


def get_local_epoch():
    epoch_time = int(time.time())
    return epoch_time


def get_time_stats():
    return {
        'local_time_ms': get_local_epoch() * 1000,
        'corrected_time_ms': get_corrected_time_ms(),
    }

def get_corrected_time_ms():
    local_time = get_local_epoch()
    try:
        global_time = get_time_difference()
    except Exception as e:
        print('Error getting global time: ', str(e))
        global_time = local_time

    return 1000 * (local_time - global_time)

def get_time_difference():
    """Return the time difference between local and global in seconds"""
    try:
        with open(TIME_DIFF_WITH_GLOBAL_FILE, 'r') as f:
            return int(f.read())
    except:
        global_epoch = get_global_epoch()
        local_epoch = get_local_epoch()
        diff = global_epoch - local_epoch
        with open(TIME_DIFF_WITH_GLOBAL_FILE, 'w') as f:
            f.write(str(diff))
        return diff


def sync_timer_clock_with_global():
    try:
        global_epoch = get_global_epoch()
        local_epoch = get_local_epoch()
        diff = global_epoch - local_epoch
    except Exception as e:
        print('Error getting global time. Will face time sync issues during mining.', str(e))
        diff = 0
    
    with open(TIME_DIFF_WITH_GLOBAL_FILE, 'w') as f:
        f.write(str(diff))
    print('Synced clock. Time difference is', diff)


if __name__ == '__main__':
    print('Time difference is ', get_time_difference())