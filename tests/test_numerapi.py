from zope.interface import implementer
from uuid import uuid4 as uuid
from datetime import datetime

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

    def __init__(self):
        self.competitions = list()

    def _create_competition(self, number: int=-1, resolved: bool=True):
        if number == -1:
            number = len(self.competitions) + 1
        self.competitions.append(MagicManager.Round(number, resolved))

    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        try:
            os.makedirs(dest_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        if not os.path.exists(dataset_path):
            shutil.copy(SAMPLE_DATA_SET_PATH, dataset_path)

    def get_leaderboard(self, _: int) -> dict:
        # TODO: only include submitted solutions during tests
        return {
          "data": {
            "rounds": [
              {
                "leaderboard": [
                  {
                    "validationLogloss": 0.6818856968749493,
                    "username": "usigma03",
                    "totalPayments": {
                      "usdAmount": "0.00",
                      "nmrAmount": "18.85"
                    },
                    "submissionId": "3983e678-05df-4dc6-b494-0a04f6d1c1fb",
                    "paymentStaking": None,
                    "paymentGeneral": None,
                    "originality": {
                      "value": True,
                      "pending": False
                    },
                    "liveLogloss": None,
                    "consistency": 100,
                    "concordance": {
                      "value": True,
                      "pending": False
                    }
                  }
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

    def get_submissions(self, submission_id: str) -> dict:
        # TODO: return true status from executor
        return {
            'data': {
                'submissions': [
                    {
                        'originality': {
                            'pending': True,
                            'value': None
                        },
                        'concordance': {
                            'pending': True,
                            'value': None
                        },
                        'consistency': True,
                        'validation_logloss': 0.693
                    }
                ]
            }
        }

    def upload_predictions(self, file_path: str) -> dict:
        # TODO: score and add to leaderboard
        submission_id = str(uuid())
        return {
            'data': {
                'create_submission': {
                    'id': submission_id
                }
            }
        }

    def raw_query(self, query, variables=None, authorization=False):
        raise NotImplementedError('do not call this method for this implementation')


def test_magic_manager_download():
    manager = MagicManager()
    import tempfile

    with tempfile.TemporaryDirectory() as dest_path:
        dataset_path = os.path.join(dest_path, 'thedata.zip')
        assert not os.path.exists(dataset_path)

        manager.download_data_set(dest_path, dataset_path)
        assert os.path.exists(dataset_path)


def test_get_leaderboard():
    api = NumerAPI(manager=MagicManager())
    lb = api.get_leaderboard(67)
    assert len(lb) > 0  # TODO: check our submission is here instead


def test_upload_predictions():
    # TODO: verify status of our upload is pending
    api = NumerAPI(manager=MagicManager())
    submission_id = api.upload_predictions('some/path.csv')
    assert len(submission_id.strip()) > 0


def test_get_competitions():
    manager = MagicManager()
    api = NumerAPI(manager=manager)
    all_competitions = api.get_competitions()
    assert isinstance(all_competitions, list)
    assert len(all_competitions) == 0

    round_number = 42
    manager._create_competition(number=round_number)

    all_competitions = api.get_competitions()
    assert isinstance(all_competitions, list)
    assert len(all_competitions) == 1
    assert all_competitions[0]['number'] == round_number


def test_download_current_dataset():
    api = NumerAPI(manager=MagicManager())
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


"""


def test_get_current_round():
    api = NumerAPI()
    current_round = api.get_current_round()
    assert current_round >= 82


def test_raw_query():
    api = NumerAPI()
    query = "query {dataset}"
    result = api.raw_query(query)
    assert isinstance(result, dict)
    assert "data" in result


def test_get_staking_leaderboard():
    api = NumerAPI()
    stakes = api.get_staking_leaderboard(82)
    # 115 people staked that round
    assert len(stakes) == 115


def test_get_submission_ids():
    api = NumerAPI()
    ids = api.get_submission_ids()
    assert len(ids) > 0
    assert isinstance(ids, dict)


def test_error_handling():
    api = NumerAPI()
    # String instead of Int
    with pytest.raises(ValueError):
        api.get_leaderboard("foo")
    # round that doesn't exist
    with pytest.raises(ValueError):
        api.get_leaderboard(-1)
    # unauthendicated request
    with pytest.raises(ValueError):
        # set wrong token
        api.token = ("foo", "bar")
        api.submission_id = 1
        api.submission_status()
"""
