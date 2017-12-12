from zope.interface import Interface


class IManager(Interface):
    def set_token(self, token: tuple):
        """
        set the token tuple (public_id, secret_key)

        :param token:
        :return:
        """

    def get_staking_leaderboard(self, round_num: int):
        """

        :param round_num:
        :return:
        """

    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        """

        :param dest_path:
        :param dataset_path:
        :return:
        """

    def get_leaderboard(self, round_num: int) -> dict:
        """

        :param round_num:
        :return:
        """

    def get_submission_ids(self):
        """
        get leaderboard submission ids for current round
        :return:
        """

    def get_current_round(self) -> dict:
        """
        get information about the current active round

        :return:
        """

    def get_competitions(self) -> dict:
        """

        get all competitions
        :return: a dict of competitions
        """

    def raw_query(self, query, variables=None, authorization=False):
        # TODO: should be split into separate methods so we know what to test for
        """

        :param query:
        :param variables:
        :param authorization:
        :return:
        """
