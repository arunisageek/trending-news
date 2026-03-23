from app.services.geo.bucket_service import BucketService


def test_bucket_service_returns_primary_and_neighbors() -> None:
    service = BucketService()
    bucket_ids = service.bucket_ids_with_neighbors(28.6139, 77.2090)
    assert len(bucket_ids) == 9
    assert len(set(bucket_ids)) == 9
