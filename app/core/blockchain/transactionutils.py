from app.config.constants import TIME_MINER_BROADCAST_INTERVAL_SECONDS
from app.core.clock.global_time import get_corrected_time_ms


def is_redundant_miner_broadcast(wallet_address, cur):
    miner_cursor = cur.execute(
        'SELECT last_broadcast_timestamp FROM miners WHERE wallet_address=?', 
        (wallet_address, )).fetchone()
    if miner_cursor is None:
        return None
    last_broadcast_timestamp = miner_cursor[0]
    current_timestamp = get_corrected_time_ms()
    # Check if the last broadcast was less than TIME_MINER_BROADCAST_INTERVAL_SECONDS / 2
    if current_timestamp - last_broadcast_timestamp < 500 * TIME_MINER_BROADCAST_INTERVAL_SECONDS:
        return False
    return True