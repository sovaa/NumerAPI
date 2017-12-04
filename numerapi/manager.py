from zope.interface import Interface


class IManager(Interface):
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

    def raw_query(self, query, variables=None, authorization=False):
        # TODO: should be split into separate methods so we know what to test for
        """

        :param query:
        :param variables:
        :param authorization:
        :return:
        """
