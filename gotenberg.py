import decimal, json

import requests
from requests.exceptions import RequestException
from requests_toolbelt.multipart.encoder import MultipartEncoder


class A4(object):
    WIDTH = 8.3
    HEIGHT = 11.7


class API(object):
    def __init__(self, schema : str='http', host : str='localhost', port : int=3000, root_path : str='/', debug : bool=False):
        self.schema = schema
        self.host = host
        self.port = port
        self.root_path = root_path

        self.debug = debug


    @property
    def root_url(self) -> str:
        return f'{self.schema}://{self.host}:{self.port}{self.root_path}'


    def concat_endpoint(self, endpoint):
        return f'{self.root_url}{endpoint}'


    def send_request(self, endpoint, files : list=[], **kwargs):
        url = self.concat_endpoint(endpoint)
        return self.send_safe_request(url=url, files=files, debug=self.debug, **kwargs)
            

    @classmethod
    def send_safe_request(cls, url, files : list=[], debug : bool=False, **kwargs):
        try:
            fields = {}
            for k, v in kwargs.items():
                if isinstance(v, (float, decimal.Decimal, int)):
                    fields[k] = str(v)
                else:
                    fields[k] = v
                    
            opened_file_list = { f'file-{i}' : ( f, open(f, 'rb') ) for i, f in enumerate(files) }
            fields.update(opened_file_list)
            
            rtn = cls._send_safe_request(url=url, **fields)
            if debug:
                print(f'Here is the data sent:')
                print(rtn.request.body)
            if rtn.status_code != 200:
                raise RequestException('API returned non 200 code', response=rtn, request=rtn.request)
        except:
            raise
        else:
            return rtn
        finally:
            [ v[1].close() for v in opened_file_list.values() ]


    @classmethod
    def _send_safe_request(cls, url, **kwargs):
        mp_encoder = MultipartEncoder(fields=kwargs)
        return requests.post(
            url=url,
            data=mp_encoder,
            headers={'Content-Type': mp_encoder.content_type}
        )


class Gotenberg(API):
    _CONVERT_ENDPOINT = 'convert'
    HTML_ENDPOINT = f'{_CONVERT_ENDPOINT}/html'
    URL_ENDPOINT = f'{_CONVERT_ENDPOINT}/url'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def convert_html(
        self,
        index_file_path : str,
        header_file_path : str = None,
        footer_file_path : str = None,
        asset_files : list = [],
        paperWidth : decimal.Decimal = A4.WIDTH,
        paperHeight : decimal.Decimal = A4.HEIGHT,
        marginTop : decimal.Decimal = 1,
        marginBottom : decimal.Decimal = 1,
        marginLeft : decimal.Decimal = 1,
        marginRight : decimal.Decimal = 1,
        landscape : bool=False,
        scale : decimal.Decimal=1,
        **kwargs,
    ) -> requests.Response:
        file_list = [ index_file_path , ]
        if header_file_path:
            file_list.append(header_file_path)
        if footer_file_path:
            file_list.append(footer_file_path)
        file_list.extend(asset_files)

        kwargs.update(
            paperWidth=paperWidth,
            paperHeight=paperHeight,
            marginTop=marginTop,
            marginBottom=marginBottom,
            marginLeft=marginLeft,
            marginRight=marginRight,
            landscape=landscape,
            scale=scale,
        )

        return self._convert_html(file_list=file_list, **kwargs)


    def _convert_html(self, file_list : list, **kwargs) -> requests.Response:
        return self.send_request(endpoint=self.HTML_ENDPOINT, files=file_list, **kwargs)


    def convert_url(
        self,
        remoteURL : str,
        paperWidth : decimal.Decimal = A4.WIDTH,
        paperHeight : decimal.Decimal = A4.HEIGHT,
        marginTop : decimal.Decimal = 1,
        marginBottom : decimal.Decimal = 1,
        marginLeft : decimal.Decimal = 1,
        marginRight : decimal.Decimal = 1,
        landscape : bool=False,
        scale : decimal.Decimal=1,
        **kwargs,
    ) -> requests.Response:

        kwargs.update(
            remoteURL=remoteURL,
            paperWidth=paperWidth,
            paperHeight=paperHeight,
            marginTop=marginTop,
            marginBottom=marginBottom,
            marginLeft=marginLeft,
            marginRight=marginRight,
            landscape=landscape,
            scale=scale,
        )

        return self._convert_url(**kwargs)


    def _convert_url(self, **kwargs) -> requests.Response:
        return self.send_request(endpoint=self.URL_ENDPOINT, **kwargs)