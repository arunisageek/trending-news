from app.utils.datetime_utils import clamp
from app.utils.geohash_utils import earth_distance_km


class DistanceService:
    def distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return earth_distance_km(lat1, lon1, lat2, lon2)

    def within_radius(self, lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
        distance = self.distance_km(lat1, lon1, lat2, lon2)
        return distance <= clamp(radius_km, 0.1, 1000.0)
