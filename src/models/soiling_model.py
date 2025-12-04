"""Soiling model for PV performance degradation.

This module will be implemented in Session 5.
"""


class SoilingModel:
    """Model for calculating soiling losses in PV systems."""

    def __init__(self, region_data):
        """Initialize the soiling model.

        Args:
            region_data: Regional soiling parameters.
        """
        self.region_data = region_data

    def calculate_soiling_loss(self, days_since_cleaning):
        """Calculate soiling loss percentage.

        Args:
            days_since_cleaning: Number of days since last cleaning.

        Returns:
            float: Soiling loss as a percentage.
        """
        # TODO: Implement in Session 5
        pass
