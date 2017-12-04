from zope.interface import Interface

from numerapi.numerapi import NumerAPI
from numerapi.manager import NumerApiManager


class IManager(Interface):
    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        """

        :param dest_path:
        :param dataset_path:
        :return:
        """

    def unzip_data_set(self, dest_path: str, dataset_path: str, dest_filename: str) -> None:
        """

        :param dest_path:
        :param dataset_path:
        :param dest_filename:
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
