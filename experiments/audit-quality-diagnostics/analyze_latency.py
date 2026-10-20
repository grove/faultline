"""Derive event-receipt intervals from archived pilot data; never run an audit."""

import hashlib
import json
from pathlib import Path


PILOT = Path(__file__).resolve().parent.parent / "real-repository-pilot"


def summarize(events):
    times = [event["received_seconds"] for event in events]
    if times != sorted(times) or not times or times[0] < 0:
        raise ValueError("Expected ordered, nonnegative event receipt times")
    if events[-1]["type"] != "turn.completed":
        raise ValueError("A complete response is required for this decomposition")
    turn = next(event["received_seconds"] for event in events if event["type"] == "turn.started")
    commands = [event for event in events if event["type"] == "item.completed"
                and event.get("item_type") == "command_execution"]
    final = [event for event in events if event["type"] == "item.completed"
             and event.get("item_type") == "agent_message"][-1]["received_seconds"]
    last_read = commands[-1]["received_seconds"]
    end = times[-1]
    if not 0 <= turn <= last_read <= final <= end:
        raise ValueError("Unexpected response/read ordering")
    starts = {event["item_id"]: event["received_seconds"] for event in events
              if event["type"] == "item.started" and event.get("item_type") == "command_execution"}
    spans = []
    for command in sorted(commands, key=lambda event: starts[event["item_id"]]):
        start, finish = starts[command["item_id"]], command["received_seconds"]
        if finish < start:
            raise ValueError("Command completion precedes its start")
        if spans and start <= spans[-1][1]:
            spans[-1][1] = max(spans[-1][1], finish)
        else:
            spans.append([start, finish])
    return {
        "end_to_end_seconds": end,
        "submission_to_turn_started_seconds": turn,
        "turn_started_to_last_read_seconds": last_read - turn,
        "last_read_to_full_final_message_seconds": final - last_read,
        "full_final_message_to_turn_completed_seconds": end - final,
        "observed_command_event_span_union_seconds": sum(finish - start for start, finish in spans),
        "read_commands": len(commands),
        "exact_repeat_commands": len(commands) - len({event["command"] for event in commands}),
        "captured_output_bytes_with_repeats": sum(event["output_bytes"] for event in commands),
        "usage_as_reported": events[-1]["usage"],
    }


def derive():
    identities, runs = {}, []
    for case in ("r1", "r2", "r3", "r4"):
        name = f"events/audit-{case}.jsonl"
        data = (PILOT / name).read_bytes()
        identities[name] = hashlib.sha256(data).hexdigest()
        runs.append({"case": case, **summarize([json.loads(line) for line in data.splitlines()])})
    return {"input_sha256": identities, "runs": runs}


if __name__ == "__main__":
    print(json.dumps(derive(), indent=2))
