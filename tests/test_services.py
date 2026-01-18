"""Unit tests for services module."""

import pytest
from datetime import datetime
from src.models import Earthquake, Treaty, ExposureAlert
from src.services import calculate_distance_km, find_exposed_treaties, summarize_exposure


class TestCalculateDistanceKm:
    """Tests for calculate_distance_km function."""

    def test_same_point_returns_zero(self):
        """Distance from a point to itself should be zero."""
        distance = calculate_distance_km(40.0, -74.0, 40.0, -74.0)
        assert distance == 0.0

    def test_known_distance_new_york_to_london(self):
        """Test with known distance: NYC to London ~5570 km."""
        # NYC: 40.7128, -74.0060
        # London: 51.5074, -0.1278
        distance = calculate_distance_km(40.7128, -74.0060, 51.5074, -0.1278)
        assert 5560 < distance < 5580  # Allow some tolerance

    def test_known_distance_tokyo_to_los_angeles(self):
        """Test with known distance: Tokyo to LA ~8815 km."""
        # Tokyo: 35.6762, 139.6503
        # LA: 34.0522, -118.2437
        distance = calculate_distance_km(35.6762, 139.6503, 34.0522, -118.2437)
        assert 8800 < distance < 8850  # Allow some tolerance


class TestFindExposedTreaties:
    """Tests for find_exposed_treaties function."""

    @pytest.fixture
    def sample_earthquake(self):
        """Sample earthquake in California."""
        return Earthquake(
            id="test1",
            magnitude=5.5,
            latitude=36.7783,
            longitude=-119.4179,
            place="Central California",
            time=datetime.now(),
            depth_km=10.0
        )

    @pytest.fixture
    def sample_treaties(self):
        """Sample treaties for testing."""
        return [
            Treaty(
                id="T001",
                name="California Quake XL",
                peril="EQ",
                region="US-CA",
                latitude=36.7783,
                longitude=-119.4179,
                radius_km=400,
                limit_usd=50_000_000
            ),
            Treaty(
                id="T002",
                name="Japan Quake QS",
                peril="EQ",
                region="JP",
                latitude=35.6762,
                longitude=139.6503,
                radius_km=500,
                limit_usd=75_000_000
            ),
        ]

    def test_earthquake_within_treaty_zone(self, sample_earthquake, sample_treaties):
        """Earthquake at treaty center should trigger alert."""
        alerts = find_exposed_treaties(sample_earthquake, sample_treaties)
        assert len(alerts) == 1
        assert alerts[0].treaty.id == "T001"
        assert alerts[0].distance_km == 0.0

    def test_earthquake_outside_all_zones(self, sample_treaties):
        """Earthquake far from all treaties should return no alerts."""
        far_earthquake = Earthquake(
            id="test2",
            magnitude=6.0,
            latitude=0.0,
            longitude=0.0,
            place="Middle of Atlantic",
            time=datetime.now(),
            depth_km=15.0
        )
        alerts = find_exposed_treaties(far_earthquake, sample_treaties)
        assert len(alerts) == 0

    def test_alerts_sorted_by_distance(self):
        """Alerts should be sorted by distance (closest first)."""
        earthquake = Earthquake(
            id="test3",
            magnitude=6.5,
            latitude=36.0,
            longitude=-119.0,
            place="Near California",
            time=datetime.now(),
            depth_km=12.0
        )
        treaties = [
            Treaty(
                id="T1",
                name="Far Treaty",
                peril="EQ",
                region="US",
                latitude=35.0,
                longitude=-118.0,
                radius_km=500,
                limit_usd=10_000_000
            ),
            Treaty(
                id="T2",
                name="Near Treaty",
                peril="EQ",
                region="US",
                latitude=36.1,
                longitude=-119.1,
                radius_km=500,
                limit_usd=20_000_000
            ),
        ]
        alerts = find_exposed_treaties(earthquake, treaties)
        assert len(alerts) == 2
        assert alerts[0].treaty.id == "T2"  # Closer treaty first


class TestSummarizeExposure:
    """Tests for summarize_exposure function."""

    def test_empty_alerts_returns_zeros(self):
        """Empty alert list should return zero summary."""
        summary = summarize_exposure([])
        assert summary["total_alerts"] == 0
        assert summary["total_exposure_usd"] == 0
        assert summary["affected_treaties"] == []
        assert summary["by_region"] == {}

    def test_single_alert_summary(self):
        """Single alert should produce correct summary."""
        earthquake = Earthquake(
            id="eq1",
            magnitude=5.0,
            latitude=36.0,
            longitude=-119.0,
            place="California",
            time=datetime.now(),
            depth_km=10.0
        )
        treaty = Treaty(
            id="T1",
            name="Test Treaty",
            peril="EQ",
            region="US-CA",
            latitude=36.0,
            longitude=-119.0,
            radius_km=100,
            limit_usd=50_000_000
        )
        alert = ExposureAlert(earthquake=earthquake, treaty=treaty, distance_km=0.0)

        summary = summarize_exposure([alert])
        assert summary["total_alerts"] == 1
        assert summary["total_exposure_usd"] == 50_000_000
        assert summary["affected_treaties"] == ["Test Treaty"]
        assert summary["by_region"] == {"US-CA": 50_000_000}

    def test_multiple_alerts_same_treaty_counted_once(self):
        """Same treaty affected by multiple earthquakes should be counted once."""
        treaty = Treaty(
            id="T1",
            name="Test Treaty",
            peril="EQ",
            region="US-CA",
            latitude=36.0,
            longitude=-119.0,
            radius_km=500,
            limit_usd=50_000_000
        )
        alerts = [
            ExposureAlert(
                earthquake=Earthquake(
                    id=f"eq{i}",
                    magnitude=5.0,
                    latitude=36.0,
                    longitude=-119.0,
                    place="California",
                    time=datetime.now(),
                    depth_km=10.0
                ),
                treaty=treaty,
                distance_km=0.0
            )
            for i in range(3)
        ]

        summary = summarize_exposure(alerts)
        assert summary["total_alerts"] == 3
        assert summary["total_exposure_usd"] == 50_000_000  # Not 150M
        assert len(summary["affected_treaties"]) == 1
