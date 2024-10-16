from season.models import Season
import logging


class SeasonService:

    @staticmethod
    def get_running_season():
        """
        Retrieves the currently running season, if any.
        """
        return Season.objects.filter(status=Season.SeasonStatus.RUNNING).first()

    @staticmethod
    def get_open_season():
        """
        Retrieves the season with an open registration, if any.
        """
        return Season.objects.filter(status=Season.SeasonStatus.OPEN).first()

    @staticmethod
    def get_previous_season():
        """
        Retrieves the most recently completed season.
        """
        return Season.objects.filter(status=Season.SeasonStatus.DONE).last()

    @staticmethod
    def get_participants(season_name):
        """
        Retrieves all participants of a season by the year (name).
        Assumes that season_name corresponds to the year.
        """
        try:
            season = Season.objects.get(year=season_name)
            return season.participants.all()
        except Season.DoesNotExist:
            logging.warning(f"No season found with year: {season_name}")
            return []

    @staticmethod
    def get_leagues(season: Season):
        """
        Retrieves all leagues associated with a given season.
        """
        return season.league_set.all()

    def get_registered_participant_count(self):
        """
        Returns the number of participants in the current open season.
        If no season is open, returns 0.
        """
        season = self.get_open_season()
        if season:
            return season.participants.count()
        else:
            logging.info("No open season found.")
            return 0

    def get_registered_participants(self):
        """
        Returns all participants registered in the current open season.
        If no season is open, returns an empty list.
        """
        season = self.get_open_season()
        if season:
            return season.participants.all()
        else:
            logging.info("No open season found.")
            return []
