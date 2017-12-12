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

    def download_data_set(self, dataset_path: str) -> None:
        """

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
        """

        :param query:
        :param variables:
        :param authorization:
        :return:
        """

    def get_submissions(self):
        """

        :return:
        """

    def get_submission(self, submission_id: str) -> dict:
        """

        :param submission_id:
        :return:
        """

    def upload_predictions(self, file_path: str) -> dict:
        """

        :param _:
        :return:
        """

    def get_user(self):
        """

        :return:
        """

    def get_payments(self):
        """

        :return:
        """

    def get_transactions(self):
        """

        :return:
        """

    def get_stakes(self):
        """

        :return:
        """

    def stake(self, confidence, value):
        """

        :param confidence:
        :param value:
        :return:
        """
