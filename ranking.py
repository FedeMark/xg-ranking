"""Contains the class to manage the logic of the ranking."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Ranking:
    def __init__(
        self,
        teams,
        starting_xG: float = 1.0,
        starting_xGA: float = 1.0,
        gamma: float = 0.01,
    ) -> None:
        """
        Args:
            gamma: weightning factor of updates
        """
        self._table = pd.DataFrame({"Team": teams})
        self._table["xOS"] = starting_xG
        self._table["xDS"] = starting_xGA
        self._gamma = gamma

    @property
    def table(self):
        return self._table.copy()

    def update_after_match(self, home: str, away: str, xG_home: float, xG_away: float):
        """
        Update function
        """
        home_row = self._table.loc[self._table.Team == home, :]
        away_row = self._table.loc[self._table.Team == away, :]

        # Compute new scores
        # V1
        # new_home_xGAR = (
        #     home_row["xDS"].values  # * (1 - self._gamma)
        #     + (xG_away - away_row["xOS"]).values * self._gamma
        # )
        # new_home_xGR = (
        #     home_row["xOS"].values  # * (1 - self._gamma)
        #     + (xG_home - away_row["xDS"]).values * self._gamma
        # )

        # new_away_xGAR = (
        #     away_row["xDS"].values  # * (1 - self._gamma)
        #     + (xG_home - home_row["xOS"]).values * self._gamma
        # )
        # new_away_xGR = (
        #     away_row["xOS"].values  # * (1 - self._gamma)
        #     + (xG_away - home_row["xDS"]).values * self._gamma
        # )

        # V2
        expected_xG_home = home_row["xOS"].iloc[0] * away_row["xDS"].iloc[0]
        expected_xG_away = home_row["xDS"].iloc[0] * away_row["xOS"].iloc[0]

        home_diff = xG_home - expected_xG_home
        away_diff = xG_away - expected_xG_away

        new_home_xDS = home_row["xDS"].iloc[0] + away_diff * self._gamma
        new_home_xOS = home_row["xOS"].iloc[0] + home_diff * self._gamma

        new_away_xDS = away_row["xDS"].iloc[0] + home_diff * self._gamma
        new_away_xOS = away_row["xOS"].iloc[0] + away_diff * self._gamma

        # Update table
        self._table.loc[self._table.Team == home, "xOS"] = new_home_xOS
        self._table.loc[self._table.Team == home, "xDS"] = new_home_xDS

        self._table.loc[self._table.Team == away, "xOS"] = new_away_xOS
        self._table.loc[self._table.Team == away, "xDS"] = new_away_xDS

    def predict_match(self, home: str, away: str, round_digits: int = 2):
        home_row = self._table.loc[self._table.Team == home, :]
        away_row = self._table.loc[self._table.Team == away, :]

        return (
            round(home_row["xOS"].iloc[0] * away_row["xDS"].iloc[0], round_digits),
            round(home_row["xDS"].iloc[0] * away_row["xOS"].iloc[0], round_digits),
        )
