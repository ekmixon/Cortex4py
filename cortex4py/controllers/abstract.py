class AbstractController(object):
    def __init__(self, endpoint, api):
        self._api = api
        self._endpoint = endpoint

    def _wrap(self, data, cls):
        if isinstance(data, dict):
            return cls(data)
        elif isinstance(data, list):
            return list(map(lambda item: cls(item), data))
        else:
            return data

    def _find_all(self, query, **kwargs):
        url = f'{self._endpoint}/_search'
        params = {k: kwargs.get(k, None) for k in ('sort', 'range')}

        return self._api.do_post(url, {'query': query or {}}, params).json()

    def _find_one_by(self, query, **kwargs):
        url = f'{self._endpoint}/_search'

        params = {
            'range': '0-1'
        }
        if 'sort' in kwargs:
            params['sort'] = kwargs['sort']

        collection = self._api.do_post(url, {'query': query or {}}, params).json()

        return collection[0] if len(collection) > 0 else None

    def _count(self, query):
        url = f'{self._endpoint}/_stats'

        payload = {
            'query': query or {},
            'stats': [{
                '_agg': 'count'
            }]
        }

        response = self._api.do_post(url, payload, {}).json()

        return response.get('count', None) if response is not None else None

    def _get_by_id(self, obj_id):
        url = f'{self._endpoint}/{obj_id}'

        return self._api.do_get(url).json()

    @staticmethod
    def _clean_changes(source, allowed, selected=[]):
        if selected is not None and len(selected) > 0:
            fields = list(set(allowed) & set(selected) & set(source.keys()))
        else:
            fields = list(set(allowed) & set(source.keys()))

        return {k: source.get(k, None) for k in fields}