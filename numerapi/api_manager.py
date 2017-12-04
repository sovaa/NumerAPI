import requests
import errno
import os

from zope.interface import implementer

from numerapi.manager import IManager

API_TOURNAMENT_URL = 'https://api-tournament.numer.ai'


@implementer(IManager)
class NumerApiManager(object):
    def __init__(self, api_url: str=API_TOURNAMENT_URL):
        self.api_url = api_url

    def download_data_set(self, dest_path: str, dataset_path: str) -> None:
        # get link to current dataset
        query = "query {dataset}"
        url = self.raw_query(query)['data']['dataset']

        # download
        dataset_res = requests.get(url, stream=True)
        dataset_res.raise_for_status()

        # create parent folder if necessary
        try:
            os.makedirs(dest_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # write dataset to file
        with open(dataset_path, "wb") as f:
            for chunk in dataset_res.iter_content(1024):
                f.write(chunk)

    def upload_predictions(self, file_path: str) -> dict:
        auth_query = \
            '''
            query($filename: String!) {
                submission_upload_auth(filename: $filename) {
                    filename
                    url
                }
            }
            '''
        variable = {'filename': os.path.basename(file_path)}
        submission_resp = self.raw_query(auth_query, variable, authorization=True)
        submission_auth = submission_resp['data']['submission_upload_auth']

        with open(file_path, 'rb') as fh:
            requests.put(submission_auth['url'], data=fh.read())

        create_query = \
            '''
            mutation($filename: String!) {
                create_submission(filename: $filename) {
                    id
                }
            }
            '''
        variables = {'filename': submission_auth['filename']}
        return self.raw_query(create_query, variables, authorization=True)

    def get_leaderboard(self, round_num: int) -> dict:
        query = '''
            query($number: Int!) {
              rounds(number: $number) {
                leaderboard {
                  consistency
                  concordance {
                    pending
                    value
                  }
                  originality {
                    pending
                    value
                  }

                  liveLogloss
                  submissionId
                  username
                  validationLogloss
                  paymentGeneral {
                    nmrAmount
                    usdAmount
                  }
                  paymentStaking {
                    nmrAmount
                    usdAmount
                  }
                  totalPayments {
                    nmrAmount
                    usdAmount
                  }
                }
              }
            }
        '''
        arguments = {'number': round_num}
        return self.raw_query(query, arguments)

    def raw_query(self, query, variables=None, authorization=False):
        # TODO: should be split into separate methods so we know what to test for
        """send a raw request to the Numerai's GraphQL API

        query (str): the query
        variables (dict): dict of variables
        authorization (bool): does the request require authorization
        """
        body = {'query': query,
                'variables': variables}
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        if authorization and self.token:
            public_id, secret_key = self.token
            headers['Authorization'] = \
                'Token {}${}'.format(public_id, secret_key)
        r = requests.post(self.api_url, json=body, headers=headers)
        result = r.json()
        if "errors" in result:
            self._handle_call_error(result['errors'])
            # fail!
            raise ValueError

        return result
