from prometheus_client import Gauge, start_http_server
SCAR_INDEX = Gauge('scar_index_current', 'Live coherence')
start_http_server(8000)
def export_scar_index(value: float):
    SCAR_INDEX.set(value)