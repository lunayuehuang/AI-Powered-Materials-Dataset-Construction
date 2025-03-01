import requests
import time

PAPER_ENDPOINT_PREFIX = 'https://api.semanticscholar.org/graph/v1/paper'
SEARCH_ENDPOINT = f'{PAPER_ENDPOINT_PREFIX}/search'

class SemanticScholar:

    def __init__(
        self, 
        limit_per_request=20, 
        sleep_seconds_per_reuqest=1, 
        apikey=None
    ):
        self.limit_per_request = limit_per_request
        self.sleep_seconds_per_reuqest = sleep_seconds_per_reuqest
        self.header = {'x-api-key': apikey} if apikey is not None else None

    def get_total_number_of_search_results(self, query):
        query_params = {
            'query': query,
            'limit': 1,
            'offset': 0,
        }
        response = requests.get(SEARCH_ENDPOINT, params=query_params, headers=self.header)
        return response.json()['total']

    def paginated_search_paper(self, query, limit, offset):
        query_params = {
            'query': query,
            'limit': limit,
            'offset': offset,
        }
        print(f'search offset = {offset}')
        response = requests.get(SEARCH_ENDPOINT, params=query_params, headers=self.header)
        while (response.status_code != 200):
            print(f'Status {response.status_code} for the failed request')
            time.sleep(self.sleep_seconds_per_reuqest)
            response = requests.get(SEARCH_ENDPOINT, params=query_params, headers=self.header)
        return [paper['paperId'] for paper in response.json()['data']]

    def get_paper(self, paperId, retry=3, timeout=15):
        url = f'{PAPER_ENDPOINT_PREFIX}/{paperId}'
        params = {'fields': 'title,year,abstract,externalIds'}
        while (retry > 0):
            response = requests.get(url, params=params, headers=self.header, timeout=timeout)
            if (response.status_code == 200):
                print(f'Found paper {paperId}')
                response_json = response.json()
                return {
                    'DOI': response_json['externalIds'].get('DOI', ''),
                    'Year': response_json.get('year', ''),
                    'Title': response_json.get('title', ''),
                    'Abstract': response_json.get('abstract', ''),
                }
            time.sleep(self.sleep_seconds_per_reuqest)            
        print(f'{paperIds} is not found after {GET_PAPER_RETRY} times retry')
        return None

    def get_papers_with_abstract(self, keywords, target_numer_of_paper, paper_ids_set, papers_with_abstract, offset=None):
        if offset is None:
            offset = 0
        total = self.get_total_number_of_search_results(keywords)
        if (total < target_numer_of_paper):
            print(f'Warning: only {total} papers are found, while the target number is {target_numer_of_paper}. Results will as many as possible.')
        while len(papers_with_abstract) < target_numer_of_paper:
            limit = min(min(self.limit_per_request, target_numer_of_paper - len(papers_with_abstract)), total - offset)
            papersIds = self.paginated_search_paper(keywords, limit, offset)
            for paperId in papersIds:
                time.sleep(self.sleep_seconds_per_reuqest)
                if paperId in paper_ids_set:
                    continue
                paper_ids_set.add(paperId)
                paper = self.get_paper(paperId)
                if paper['Abstract'] is not None and paper['Abstract'] != '':
                    papers_with_abstract.append(paper.copy())
            offset += limit
            print(f'Now we have {len(papers_with_abstract)} papers with abstracts !')
        return


        


    