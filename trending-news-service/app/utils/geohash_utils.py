from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt


@dataclass(frozen=True)
class Bucket:
    lat_index: int
    lon_index: int
    cell_km: float

    @property
    def bucket_id(self) -> str:
        return f"{self.lat_index}:{self.lon_index}:{round(self.cell_km, 3)}"


def _cell_degrees(cell_km: float) -> float:
    return cell_km / 111.0


def bucket_from_coordinates(lat: float, lon: float, cell_km: float) -> Bucket:
    cell_deg = _cell_degrees(cell_km)
    lat_index = int((lat + 90.0) // cell_deg)
    lon_index = int((lon + 180.0) // cell_deg)
    return Bucket(lat_index=lat_index, lon_index=lon_index, cell_km=cell_km)


def neighboring_buckets(bucket: Bucket) -> list[Bucket]:
    neighbors: list[Bucket] = []
    for lat_delta in (-1, 0, 1):
        for lon_delta in (-1, 0, 1):
            if lat_delta == 0 and lon_delta == 0:
                continue
            neighbors.append(
                Bucket(
                    lat_index=bucket.lat_index + lat_delta,
                    lon_index=bucket.lon_index + lon_delta,
                    cell_km=bucket.cell_km,
                )
            )
    return neighbors


def neighboring_bucket_ids_map(bucket: Bucket) -> dict[str, float]:
    weights = {bucket.bucket_id: 1.0}
    for neighbor in neighboring_buckets(bucket):
        weights[neighbor.bucket_id] = 0.8
    return weights


def earth_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_km * c
