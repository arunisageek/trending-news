from app.core.config import get_settings
from app.utils.geohash_utils import Bucket, bucket_from_coordinates, neighboring_buckets


class BucketService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def bucket(self, lat: float, lon: float) -> Bucket:
        return bucket_from_coordinates(lat, lon, self.settings.bucket_cell_km)

    def bucket_id(self, lat: float, lon: float) -> str:
        return self.bucket(lat, lon).bucket_id

    def bucket_ids_with_neighbors(self, lat: float, lon: float) -> list[str]:
        primary = self.bucket(lat, lon)
        neighbors = neighboring_buckets(primary)
        ids = [primary.bucket_id]
        ids.extend([bucket.bucket_id for bucket in neighbors])
        return ids
