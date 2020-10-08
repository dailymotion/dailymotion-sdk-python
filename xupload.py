import aiohttp
import aiofiles
import asyncio
import os


class Xupload(object):

    PROXY_SOCKET = ""
    _QUERY_TIMEOUT = 60 * 60
    _CHUNK_SIZE = 4 << 20

    def __init__(self, upload_url, file_path, workers=1, headers=None, progress=None):
        if not os.path.exists(file_path):
            raise IOError("[Errno 2] No such file or directory: '%s'" % file_path)

        self._url = upload_url
        self._file_path = file_path
        self._file_size = os.stat(self._file_path).st_size
        self._workers = int(max(1, min(workers, self._file_size / self._CHUNK_SIZE, 8)))
        self._headers = headers if isinstance(headers,dict) else {}
        self._progress = progress
        self._chunk_size = self._file_size / self._workers
        self._chunk_size = (
            int(self._chunk_size / int(self._chunk_size / self._CHUNK_SIZE))
            if int(self._chunk_size / self._CHUNK_SIZE) > 0
            else int(self._chunk_size)
        )
        self._session = None
        self._clients = []
        self._tasks = []
        chunks = int(round(self._file_size / self._chunk_size / self._workers))

        for index in range(self._workers):
            start = index * self._chunk_size * chunks
            end = (
                self._file_size - 1
                if index == self._workers - 1
                else ((index + 1) * self._chunk_size * chunks) - 1
            )
            self._clients.append({
                'start': start,
                'offset': start,
                'end': end,
                'size': 0,
                'sent': 0
            })

    def start(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self._run())
        loop.run_until_complete(asyncio.sleep(0.250))
        loop.close()
        return result

    async def _prepare_handle(self, client):
        async with aiofiles.open(self._file_path, "rb") as file:
            client['size'] = min(self._chunk_size, client['end'] - client['offset'] + 1)
            client['data'] = await self._get_file_chunk(file, client['size'], client['offset'])
            client['headers'] = {
                **self._headers,
                **{
                    'Accept': '*/*',
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': 'attachment; filename="{}"'.format(
                        os.path.basename(self._file_path)
                    ),
                    'Content-Range': 'bytes {}-{}/{}'.format(
                        client['offset'],
                        client['offset'] + client['size'] - 1,
                        self._file_size
                    )
                }
            }
            self._tasks.append(
                asyncio.ensure_future(self._post_chunk(self._url, client))
            )

    async def _run(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self._QUERY_TIMEOUT),
            connector=aiohttp.TCPConnector(limit=self._workers)
        )

        if self._progress:
            self._progress(0, self._file_size)

        async with self._session:
            for client in self._clients:
                await self._prepare_handle(client)

            while len(self._tasks) > 0:
                await asyncio.sleep(0.3)
                for task in self._tasks:
                    if task.done():
                        self._tasks.remove(task)
                        result = task.result()
                        exception = task.exception()

                        if result['status'] == 200:
                            if self._progress:
                                self._progress(self._file_size, self._file_size)
                            return result["content"]
                        if result['status'] in (202, 416):
                            client = self._get_client_from_request(result['request_info'])
                            client['sent'] += client['size']

                            if self._progress:
                                sent = 0
                                for c in self._clients:
                                    sent += c['sent']
                                self._progress(min(sent,self._file_size), self._file_size)

                            ranges = []
                            range_header = result['headers'].get('Range').split('/')
                            if len(range_header) > 0:
                                ranges = [r.split('-') for r in range_header[0].split(',')]

                            for r_start, r_end in [[int(i), int(j)] for i,j in ranges]:
                                if client['start'] >= r_start and client['start'] < r_end:
                                    if client['end'] <= r_end:
                                        break
                                    if (r_end - client['start'] + 1) % self._chunk_size == 0:
                                        client['offset'] = r_end + 1
                                        await self._prepare_handle(client)
                                        break
                        elif 'content' in result and 'error' in result['content']:
                            return result['content']

                        if exception:
                            raise DailymotionXuploadError(str(exception))

    def _get_client_from_request(self, request_info):
        for client in self._clients:
            if client['headers']['Content-Range'] == request_info.headers['Content-Range']:
                return client

    @staticmethod
    def print_progress(current, total):
        """
        Example of function which prints the percentage of progression
        :param current: current bytes sent
        :param total: total bytes
        :return: None
        """
        percent = int(min((current * 100) / total, 100))

        print(
            "[{}{}] {}%\r".format(
                "*" * int(percent), " " * (100 - int(percent)), percent
            ),
            flush=True,
            end="",
        )

    async def _post_chunk(self, url, client):
        async with self._session.post(
            url,
            data=client["data"],
            headers=client["headers"],
            proxy=self.PROXY_SOCKET,
            expect100=True,
        ) as resp:
            return {
                "status": resp.status,
                "headers": resp.headers,
                "content": await resp.json(),
                "request_info": resp.request_info,
            }

    async def _get_file_chunk(self, file, chunk_length, chunk_start=0):
        await file.seek(chunk_start)
        return await file.read(chunk_length)


class DailymotionXuploadError(Exception):
    pass
