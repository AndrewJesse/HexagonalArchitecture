from logic.transform import Payload, normalize

from application.ports import DataSource, DataSink


def run(source: DataSource, sink: DataSink) -> Payload:
    raw = source.read()
    out = normalize(raw)
    sink.write(out)
    return out
