from abc import ABC, abstractmethod
import asyncio
import aiohttp

class IHttpClient(ABC):
    @abstractmethod
    async def get(self, url, data=None):
        pass

    @abstractmethod
    async def post(self, url, data=None):
        pass

    @abstractmethod
    async def put(self, url, data=None):
        pass

    @abstractmethod
    async def patch(self, url, data=None):
        pass

    @abstractmethod
    async def delete(self, url, data=None):
        pass

class HttpClient(IHttpClient):
    '''
    https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.put
    '''
    def __init__(self, return_type="json"):
        self._client = aiohttp.ClientSession()
        self._headers: dict = {}
        self._return_type: str = return_type
        self._response: aiohttp.ClientResponse = None

    @property
    def response(self):
        return self._response
    
    def set_headers(self, **kwargs: dict[str, any]):
        # for key, val in kwargs.items():
        #     self._headers[key] = val
        self._headers = headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNmQyYmMxM2UxODFjZTQ5NjE2NjE3MDg2NTgzNDE1ZiIsInN1YiI6IjY2MTFiN2M4MTEwOGE4MDEzMThiZDc4ZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.J0h34JFPSRjlx5vvzDnU2n_7PQDHhNfezE43mQuefEw"
        }

    def set_options(self, **kwargs):
        pass

    def set_params(self, **kwargs):
        pass
    
    def _get_response(self):
        if self._response.status not in {200, 201}:
            raise RuntimeError(f"Error: {self._response.status}")
        
        if self._return_type == "json":
            return self._response.json()
        elif self._return_type == "text":
            return self._response.text()
        elif self._return_type == "binary":
            return self._response.read()
        else:
            return self._response.json()
    
    async def on_request_start(session, context, params):
        print(f"Start request: {params.url}")

    async def on_request_end(session, context, params):
        print(f"End request: {params.url}")

    async def get(self, url, params=None):
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(self.on_request_start)
        trace_config.on_request_end.append(self.on_request_end)
        async with aiohttp.ClientSession(headers=self._headers, trace_configs=[trace_config]) as client:
            async with client.get(url, params=params) as response:
                # self._response = response
                # return self._get_response()
                return await response.json()
            
    async def post(self, url, data=None):
        async with self._client as client:
            async with client.post(url, headers=self._headers, data=data) as response:
                self._response = await response
                return self._get_response()

    async def put(self, url, data=None):
        async with self._client as client:
            async with client.put(url=url, headers=self._headers, data=data) as response:
                self._response = await response
                return self._get_response()

    async def patch(self, url, data=None):
        async with self._client as client:
            async with client.patch(url=url, headers=self._headers, data=data) as response:
                self._response = await response
                return self._get_response()

    async def delete(self, url, data=None):
        async with self._client as client:
            async with client.delete(url=url, headers=self._headers, data=data) as response:
                self._response = await response
                return self._get_response()

    '''
    url = 'http://httpbin.org/post'
    files = {'file': open('report.xls', 'rb')}
    await session.post(url, data=files)
    ----------------------------------------
    url = 'http://httpbin.org/post'
    data = aiohttp.FormData()
    data.add_field('
        file',
        open('report.xls', 'rb'),
        filename='report.xls',
        content_type='application/vnd.ms-excel'
    )
    await session.post(url, data=data)
    '''