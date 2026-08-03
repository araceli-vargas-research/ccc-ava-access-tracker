from __future__ import annotations

import argparse
import math
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Iterator

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAYMO_SOURCE = PROJECT_ROOT / "vendor" / "waymo-open-dataset" / "src"

if WAYMO_SOURCE.exists():
    sys.path.insert(0, str(WAYMO_SOURCE))

try:
    from waymo_open_dataset.protos import scenario_pb2
except ImportError as exc:
    raise SystemExit(
        "\nCould not import Waymo's Scenario protobuf.\n"
        "Complete the setup commands below before running this script.\n"
    ) from exc


DEFAULT_INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "waymo_open_dataset"
    / "motion"
    / "validation"
)

DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "waymo_scenario_metrics.parquet"
)


OBJECT_TYPE_NAMES = {
    0: "unset",
    1: "vehicle",
    2: "pedestrian",
    3: "cyclist",
    4: "other",
}


def read_tfrecord(path: Path) -> Iterator[bytes]:
    """
    Read uncompressed TFRecord entries without requiring TensorFlow.

    TFRecord layout:
        uint64 record length
        uint32 masked CRC for length
        bytes record
        uint32 masked CRC for record
    """
    with path.open("rb") as file:
        record_number = 0

        while True:
            length_bytes = file.read(8)

            if not length_bytes:
                break

            if len(length_bytes) != 8:
                raise ValueError(
                    f"Incomplete TFRecord length header in {path.name}"
                )

            record_length = struct.unpack("<Q", length_bytes)[0]

            length_crc = file.read(4)
            if len(length_crc) != 4:
                raise ValueError(
                    f"Incomplete length checksum in {path.name}"
                )

            record = file.read(record_length)
            if len(record) != record_length:
                raise ValueError(
                    f"Incomplete record {record_number} in {path.name}"
                )

            data_crc = file.read(4)
            if len(data_crc) != 4:
                raise ValueError(
                    f"Incomplete data checksum in {path.name}"
                )

            yield record
            record_number += 1


def valid_states(track) -> list:
    return [state for state in track.states if state.valid]


def state_speed(state) -> float:
    return math.hypot(state.velocity_x, state.velocity_y)


def count_map_features(scenario) -> Counter:
    counts: Counter = Counter()

    for feature in scenario.map_features:
        feature_type = feature.WhichOneof("feature_data")

        if feature_type:
            counts[feature_type] += 1
        else:
            counts["unknown"] += 1

    return counts


def count_traffic_signals(scenario) -> tuple[int, int]:
    """
    Returns:
        unique signal-controlled lane count,
        total observed lane-state records
    """
    unique_lane_ids: set[int] = set()
    observations = 0

    for dynamic_state in scenario.dynamic_map_states:
        for lane_state in dynamic_state.lane_states:
            unique_lane_ids.add(lane_state.lane)
            observations += 1

    return len(unique_lane_ids), observations


def build_complexity_index(
    *,
    vehicle_count: int,
    pedestrian_count: int,
    cyclist_count: int,
    moving_agent_count: int,
    lane_count: int,
    crosswalk_count: int,
    traffic_signal_count: int,
) -> float:
    """
    Transparent, constructed index for dashboard exploration.

    This is not a Waymo performance or safety score.
    """
    score = (
        0.40 * vehicle_count
        + 2.50 * pedestrian_count
        + 2.50 * cyclist_count
        + 0.35 * moving_agent_count
        + 0.08 * lane_count
        + 1.50 * crosswalk_count
        + 1.25 * traffic_signal_count
    )

    return round(min(score, 100.0), 2)


def summarize_scenario(
    scenario,
    *,
    shard_name: str,
    record_number: int,
) -> dict:
    object_counts: Counter = Counter()
    speeds: list[float] = []
    moving_agent_count = 0
    valid_agent_count = 0

    for track in scenario.tracks:
        object_type = OBJECT_TYPE_NAMES.get(
            int(track.object_type),
            "unknown",
        )
        object_counts[object_type] += 1

        states = valid_states(track)

        if not states:
            continue

        valid_agent_count += 1
        track_speeds = [state_speed(state) for state in states]
        speeds.extend(track_speeds)

        # An agent is considered moving if it exceeds 1 m/s
        # at any valid point in the scenario.
        if max(track_speeds, default=0.0) >= 1.0:
            moving_agent_count += 1

    map_counts = count_map_features(scenario)

    traffic_signal_count, traffic_signal_observations = (
        count_traffic_signals(scenario)
    )

    timestamps = list(scenario.timestamps_seconds)

    if len(timestamps) >= 2:
        duration_seconds = timestamps[-1] - timestamps[0]
    else:
        duration_seconds = 0.0

    vehicle_count = object_counts["vehicle"]
    pedestrian_count = object_counts["pedestrian"]
    cyclist_count = object_counts["cyclist"]
    lane_count = map_counts["lane"]
    crosswalk_count = map_counts["crosswalk"]

    current_time_seconds = None

    if (
        timestamps
        and 0 <= scenario.current_time_index < len(timestamps)
    ):
        current_time_seconds = timestamps[scenario.current_time_index]

    return {
        "scenario_id": scenario.scenario_id,
        "source_shard": shard_name,
        "record_number": record_number,
        "duration_seconds": round(duration_seconds, 3),
        "time_step_count": len(timestamps),
        "current_time_index": scenario.current_time_index,
        "current_time_seconds": current_time_seconds,
        "total_track_count": len(scenario.tracks),
        "valid_agent_count": valid_agent_count,
        "moving_agent_count": moving_agent_count,
        "vehicle_count": vehicle_count,
        "pedestrian_count": pedestrian_count,
        "cyclist_count": cyclist_count,
        "other_agent_count": object_counts["other"],
        "lane_count": lane_count,
        "road_line_count": map_counts["road_line"],
        "road_edge_count": map_counts["road_edge"],
        "stop_sign_count": map_counts["stop_sign"],
        "crosswalk_count": crosswalk_count,
        "speed_bump_count": map_counts["speed_bump"],
        "driveway_count": map_counts["driveway"],
        "unknown_map_feature_count": map_counts["unknown"],
        "traffic_signal_count": traffic_signal_count,
        "traffic_signal_observations": traffic_signal_observations,
        "mean_agent_speed_mps": (
            round(sum(speeds) / len(speeds), 3)
            if speeds
            else 0.0
        ),
        "maximum_agent_speed_mps": (
            round(max(speeds), 3)
            if speeds
            else 0.0
        ),
        "objects_of_interest_count": len(
            scenario.objects_of_interest
        ),
        "tracks_to_predict_count": len(
            scenario.tracks_to_predict
        ),
        "sdc_track_index": scenario.sdc_track_index,
        "complexity_index_v1": build_complexity_index(
            vehicle_count=vehicle_count,
            pedestrian_count=pedestrian_count,
            cyclist_count=cyclist_count,
            moving_agent_count=moving_agent_count,
            lane_count=lane_count,
            crosswalk_count=crosswalk_count,
            traffic_signal_count=traffic_signal_count,
        ),
    }


def process_files(
    input_dir: Path,
    output_path: Path,
    max_scenarios: int | None,
) -> pd.DataFrame:
    shard_paths = sorted(input_dir.glob("validation.tfrecord-*"))

    if not shard_paths:
        raise FileNotFoundError(
            f"No TFRecord shards found in:\n{input_dir}"
        )

    print(f"Found {len(shard_paths)} TFRecord shards.")

    rows: list[dict] = []
    processed = 0

    for shard_number, shard_path in enumerate(shard_paths, start=1):
        print(
            f"\nReading shard {shard_number}/{len(shard_paths)}: "
            f"{shard_path.name}"
        )

        for record_number, serialized_record in enumerate(
            read_tfrecord(shard_path)
        ):
            scenario = scenario_pb2.Scenario()

            try:
                scenario.ParseFromString(serialized_record)
            except Exception as exc:
                print(
                    f"Skipping record {record_number} in "
                    f"{shard_path.name}: {exc}"
                )
                continue

            rows.append(
                summarize_scenario(
                    scenario,
                    shard_name=shard_path.name,
                    record_number=record_number,
                )
            )

            processed += 1

            if processed % 50 == 0:
                print(f"Processed {processed} scenarios.")

            if (
                max_scenarios is not None
                and processed >= max_scenarios
            ):
                break

        if (
            max_scenarios is not None
            and processed >= max_scenarios
        ):
            break

    if not rows:
        raise RuntimeError("No scenarios were successfully processed.")

    dataframe = pd.DataFrame(rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_parquet(output_path, index=False)

    csv_path = output_path.with_suffix(".csv")
    dataframe.to_csv(csv_path, index=False)

    print("\nProcessing complete.")
    print(f"Scenarios processed: {len(dataframe):,}")
    print(f"Parquet: {output_path}")
    print(f"CSV: {csv_path}")

    return dataframe


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert Waymo Motion Scenario TFRecords into "
            "dashboard-friendly tables."
        )
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Folder containing validation TFRecord shards.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination Parquet file.",
    )

    parser.add_argument(
        "--max-scenarios",
        type=int,
        default=500,
        help=(
            "Maximum scenarios to process. "
            "Use 0 to process every downloaded shard."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    max_scenarios = (
        None if args.max_scenarios == 0 else args.max_scenarios
    )

    process_files(
        input_dir=args.input_dir,
        output_path=args.output,
        max_scenarios=max_scenarios,
    )


if __name__ == "__main__":
    main()