from abc import ABC
from abc import abstractmethod


class NumerManager(ABC):
    @abstractmethod
    def set_token(self, token: tuple):
        """
        set the token tuple (public_id, secret_key)

        :param token:
        :return:
        """

    @abstractmethod
    def get_staking_leaderboard(self, round_num: int):
        """
        expects the following type of result:

        {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "validationLogloss": 0.6863094945379241,
                    "username": "doomgloom",
                    "stake": {
                      "value": null,
                      "txHash": null,
                      "soc": null,
                      "insertedAt": null,
                      "confidence": null
                    },
                    "liveLogloss": null,
                    "consistency": 91.66666666666666
                  },
                  {
                    "validationLogloss": 0.6945099681690601,
                    "username": "jenson3",
                    "stake": {
                      "value": null,
                      "txHash": null,
                      "soc": null,
                      "insertedAt": null,
                      "confidence": null
                    },
                    "liveLogloss": null,
                    "consistency": 75
                  }
                ]
              }
            ]
          }
        }

        :param round_num:
        :return:
        """

    @abstractmethod
    def download_data_set(self, dataset_path: str) -> None:
        """

        :param dataset_path:
        :return:
        """

    @abstractmethod
    def get_leaderboard(self, round_num: int) -> dict:
        """

        :param round_num:
        :return:
        """

    @abstractmethod
    def get_submission_ids(self):
        """
        get leaderboard submission ids for current round

        NumerAPI expects the manager to query for this:

        query {
              rounds(number: 0) {
                leaderboard {
                  username
                  submissionId
                }
            }
        }

        which returns this:

        {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "username": "network1",
                    "submissionId": "2a0e7b93-75e5-4e3a-b1fb-7e94bc0941e7"
                  },
                  {
                    "username": "smile1",
                    "submissionId": "61225cb4-0723-487b-8ae4-534298b2fdbd"
                  }
              }
            ]
          }
        }

        :return:
        """

    @abstractmethod
    def get_current_round(self) -> dict:
        """
        get information about the current active round

        :return:
        """

    @abstractmethod
    def get_competitions(self) -> dict:
        """

        get all competitions
        :return: a dict of competitions
        """

    @abstractmethod
    def raw_query(self, query, variables=None, authorization=False):
        """

        :param query:
        :param variables:
        :param authorization:
        :return:
        """

    @abstractmethod
    def get_submission(self, submission_id: str) -> dict:
        """

        :param submission_id:
        :return:
        """

    @abstractmethod
    def upload_predictions(self, file_path: str) -> dict:
        """

        :param _:
        :return:
        """

    @abstractmethod
    def get_user(self):
        """
        expects this:
        query {
            user {
              username
              banned
              assignedEthAddress
              availableNmr
              availableUsd
              email
              id
              mfaEnabled
              status
              insertedAt
              apiTokens {
                name
                public_id
                scopes
              }
            }
          }

        :return:
        """

    @abstractmethod
    def get_payments(self):
        """

        :return:
        """

    @abstractmethod
    def get_transactions(self):
        """

        :return:
        """

    @abstractmethod
    def get_stakes(self):
        """

        :return:
        """

    @abstractmethod
    def stake(self, confidence, value):
        """

        :param confidence:
        :param value:
        :return:
        """
