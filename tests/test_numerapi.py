# method names of pytest fixtures has (for some reason) no prefix, resulting in "shadows name from outer scope"
# pylint: disable=redefined-outer-name

from zope.interface import implementer
from uuid import uuid4 as uuid
from datetime import datetime
from typing import Generator

import pytest
import shutil
import errno
import os

from numerapi import NumerAPI
from numerapi.manager import IManager

SAMPLE_DATA_SET_PATH = 'tests/data/numerai_dataset.zip'
SAMPLE_DATA_DIR = 'tests/data/'
SAMPLE_TRAIN_FILE = 'sample_training.csv.bz2'
SAMPLE_TOURN_FILE = 'sample_tournament.csv.bz2'
SAMPLE_RESULT_FILE = 'sample_result.csv.bz2'

NAME_TRAIN_CSV = 'numerai_training_data.csv'
NAME_TOURN_CSV = 'numerai_tournament_data.csv'

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


@implementer(IManager)
class MagicManager(object):
    class Round(object):
        def __init__(self, number: int=1, resolved: bool=True):
            self.number = number
            self.resolved_staking = resolved
            self.resolved_general = resolved
            self.resolve_time = datetime.utcnow().strftime(DATE_FORMAT)
            self.open_time = datetime.utcnow().strftime(DATE_FORMAT)
            self.dataset_id = str(uuid())

        def to_json(self):
            return {
                "resolvedStaking": self.resolved_staking,
                "resolvedGeneral": self.resolved_general,
                "resolveTime": self.resolve_time,
                "openTime": self.open_time,
                "number": self.number,
                "datasetId": self.dataset_id
            }

    class Leaderboard(object):
        def __init__(self):
            self.submissions = list()

    class Submission(object):
        def __init__(self, username: str):
            self.username = username
            self.submission_id = str(uuid())
            self.validation_logloss = 0.0
            self.total_pay_usd = None
            self.total_pay_nmr = None
            self.payment_staking = None
            self.payment_general = None
            self.originality_value = False
            self.originality_pending = True
            self.live_logloss = None
            self.consistency = None
            self.concordance_value = False
            self.concordance_pending = True

        def set_as_done(self):
            self.validation_logloss = 0.6931471805599453
            self.concordance_pending = False
            self.concordance_value = True
            self.originality_pending = False
            self.originality_value = True
            self.consistency = True

    def __init__(self):
        self.competitions = list()
        self.leaderboards = dict()
        self.stakes = list()
        self.user_id = None
        self.user_name = None

    def set_token(self, token: tuple):
        if token is None:
            self.user_id = 'foo'
            self.user_name = 'foo'
            return

        # only need the user_id
        self.user_id, _ = token
        self.user_name = self.user_id

    def create_competition(self, number: int=-1, resolved: bool=True):
        if number == -1:
            number = len(self.competitions) + 1

        if number in self.leaderboards.keys():
            raise RuntimeError('round "%s" already exists' % str(number))

        self.leaderboards[number] = MagicManager.Leaderboard()
        self.competitions.append(MagicManager.Round(number, resolved))

    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        try:
            os.makedirs(dest_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        if not os.path.exists(dataset_path):
            shutil.copy(SAMPLE_DATA_SET_PATH, dataset_path)

    @staticmethod
    def type_hint_submissions(submissions: list) -> Generator[Submission, None, None]:
        for submission in submissions:
            yield submission

    def get_leaderboard(self, round_id: int) -> dict:
        if round_id not in self.leaderboards:
            raise ValueError('no such round "%s"' % str(round_id))

        return {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "validationLogloss": submission.validation_logloss,
                    "username": submission.username,
                    "totalPayments": {
                      "usdAmount": submission.total_pay_usd,
                      "nmrAmount": submission.total_pay_nmr
                    },
                    "submissionId": submission.submission_id,
                    "paymentStaking": submission.payment_staking,
                    "paymentGeneral": submission.payment_general,
                    "originality": {
                      "value": submission.originality_value,
                      "pending": submission.originality_pending
                    },
                    "liveLogloss": submission.live_logloss,
                    "consistency": submission.consistency,
                    "concordance": {
                      "value": submission.concordance_value,
                      "pending": submission.concordance_pending
                    }
                  } for submission in MagicManager.type_hint_submissions(self.leaderboards[round_id].submissions)
                ]
              }
            ]
          }
        }

    def get_competitions(self) -> dict:
        return {
            'data': {
                'rounds': [
                    competition.to_json() for competition in self.competitions
                ]
            }
        }

    def get_submissions(self):
        """
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
        """
        current_round_id = self.get_current_round()['data']['rounds'][0]['number']

        return {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "username": submission.username,
                    "submissionId": submission.submission_id
                  } for submission in MagicManager.type_hint_submissions(
                        self.leaderboards[current_round_id].submissions)
                ]
              }
            ]
          }
        }

    def get_current_round(self) -> dict:
        rounds = self.competitions.copy()

        if len(rounds) > 0:
            rounds.sort(key=lambda r: r.number, reverse=True)
            number = rounds[0].number
        else:
            number = -1

        return {
            "data": {
                "rounds": [
                    {
                        "number": number
                    }
                ]
            }
        }

    def get_submission(self, submission_id: str) -> dict:
        current_round_id = self.get_current_round()['data']['rounds'][0]['number']

        submission: MagicManager.Submission = None
        for sub in self.leaderboards[current_round_id].submissions:
            if submission.submission_id == submission_id:
                submission = sub

        if submission is None:
            raise ValueError('no such submission "%s"' % str(submission_id))

        return {
            'data': {
                'submissions': [
                    {
                        'originality': {
                            'pending': submission.originality_pending,
                            'value': submission.originality_value
                        },
                        'concordance': {
                            'pending': submission.concordance_pending,
                            'value': submission.concordance_value
                        },
                        'consistency': submission.consistency,
                        'validation_logloss': submission.validation_logloss
                    }
                ]
            }
        }

    def upload_predictions(self, _: str) -> dict:
        current_round = self.get_current_round()
        round_id = current_round['data']['rounds'][0]["number"]
        if round_id == -1:
            raise RuntimeError('before testing upload, create at least one competition first')

        submission = MagicManager.Submission(username=self.user_id)
        self.leaderboards[round_id].submissions.append(submission)

        return {
            'data': {
                'create_submission': {
                    'id': submission.submission_id
                }
            }
        }

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
        if round_num not in self.stakes:
            return {
              "data": {
                "rounds": [
                  {
                    "leaderboard": []
                  }
                ]
              }
            }

        return {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "validationLogloss": stake.validation_logloss,
                    "username": stake.user_name,
                    "stake": {
                      "value": stake.value,
                      "txHash": stake.tx_hash,
                      "soc": stake.soc,
                      "insertedAt": stake.inserted_at,
                      "confidence": stake.confidence
                    },
                    "liveLogloss": stake.live_logloss,
                    "consistency": stake.consistency
                  } for stake in self.stakes[round_num]
                ]
              }
            ]
          }
        }

    def raw_query(self, query, variables=None, authorization=False):
        raise NotImplementedError('do not call this method for this implementation')


@pytest.fixture(name='api', scope='function')
def fixture_for_api():
    magic_manager = MagicManager()
    magic_manager.create_competition(0, resolved=False)
    return NumerAPI(public_id='foo', secret_key='bar', manager=magic_manager)


def test_magic_manager_download(api: NumerAPI):
    import tempfile

    with tempfile.TemporaryDirectory() as dest_path:
        data_set_path = os.path.join(dest_path, 'thedata.zip')
        assert not os.path.exists(data_set_path)

        api.manager.download_data_set(dest_path, data_set_path)
        assert os.path.exists(data_set_path)


def test_get_leaderboard_returns_empty_list():
    # don't use fixture here, create our own competition
    api = NumerAPI(manager=MagicManager())
    api.manager.create_competition(number=67)
    lb = api.get_leaderboard(67)
    assert isinstance(lb, list)
    assert len(lb) == 0


def test_upload_predictions_returns_id(api: NumerAPI):
    submission_id = api.upload_predictions('some/path.csv')
    assert isinstance(submission_id, str)
    assert len(submission_id.strip()) > 0


def test_get_submission_after_upload(api: NumerAPI):
    submission_id = api.upload_predictions('some/path.csv')
    lb = api.get_leaderboard()
    assert isinstance(lb, list)
    assert len(lb) == 1
    assert lb[0]['submissionId'] == submission_id


def test_get_competitions():
    # don't use fixtures here, create our own competitions
    api = NumerAPI(manager=MagicManager())
    all_competitions = api.get_competitions()
    assert isinstance(all_competitions, list)
    assert len(all_competitions) == 0

    round_number = 42
    api.manager.create_competition(number=round_number)

    all_competitions = api.get_competitions()
    assert isinstance(all_competitions, list)
    assert len(all_competitions) == 1
    assert all_competitions[0]['number'] == round_number


def test_download_current_dataset(api: NumerAPI):
    directory = None
    csv_files = ['numerai_tournament_data.csv', 'numerai_training_data.csv']

    try:
        path = api.download_current_dataset(unzip=True)
        assert os.path.exists(path)
        directory = path.replace(".zip", "")

        for csv_file in csv_files:
            final_path_name = os.path.join(directory, csv_file)
            assert os.path.exists(final_path_name)
    finally:
        if directory is not None:
            for csv_file in csv_files:
                os.remove(os.path.join(directory, csv_file))

            os.removedirs(os.path.join(directory, 'numerai_dataset'))
            os.remove('%s.zip' % directory)


def test_get_current_round():
    # don't use fixture here, create our own rounds
    api = NumerAPI(public_id='foo', secret_key='bar', manager=MagicManager())
    api.manager.create_competition(number=1)
    current_round = api.get_current_round()
    assert current_round == 1

    api.manager.create_competition(number=2)
    current_round = api.get_current_round()
    assert current_round == 2


def test_upload_submission_returns_submission_id(api: NumerAPI):
    submission_id = api.upload_predictions('foo')
    assert isinstance(submission_id, str)
    assert len(submission_id) > 0


def test_get_submission_ids_empty_before_upload(api: NumerAPI):
    ids = api.get_submission_ids()
    assert len(ids) == 0


def test_get_submission_ids_contains_uploaded_submission(api: NumerAPI):
    submission_id = api.upload_predictions('foo')
    ids = api.get_submission_ids()
    assert len(ids) == 1
    assert isinstance(ids, dict)
    assert api.manager.user_name in ids
    assert ids[api.manager.user_name] == submission_id


def test_get_staking_leaderboard_no_submissions(api: NumerAPI):
    stakes = api.get_staking_leaderboard(82)
    assert len(stakes) == 0


def test_error_handling_get_leaderboard_str_id(api: NumerAPI):
    # String instead of Int
    with pytest.raises(ValueError):
        api.get_leaderboard("foo")


def test_error_handling_get_leaderboard_unknown_round_id(api: NumerAPI):
    # round that doesn't exist
    with pytest.raises(ValueError):
        api.get_leaderboard(-1)


"""

def test_error_handling_submission_status_no_auth(api: NumerAPI):
    # unauthenticated request
    with pytest.raises(ValueError):
        # set wrong token
        api.token = ("foo", "bar")
        api.submission_id = 1
        api.submission_status()

def test_raw_query():
    api = NumerAPI()
    query = "query {dataset}"
    result = api.raw_query(query)
    assert isinstance(result, dict)
    assert "data" in result




"""
