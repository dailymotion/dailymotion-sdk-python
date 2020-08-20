import aiohttp
import aiofiles
import asyncio
import os


class Xupload(object):

    PROXY_SOCKET = ""
    _QUERY_TIMEOUT = 60 * 60
    _CHUNK_SIZE = 4 << 20

    def __init__(self, upload_url, file_path, workers=1, headers={}, progress=None):
        if not os.path.exists(file_path):
            raise IOError("[Errno 2] No such file or directory: '%s'" % file_path)

        self._url = upload_url
        self._file_path = file_path
        self._file_size = os.stat(self._file_path).st_size
        self._workers = int(max(1, min(workers, self._file_size / self._CHUNK_SIZE, 8)))
        self._headers = headers
        self._progress = progress
        self._chunk_size = self._file_size / self._workers
        self._chunk_size = (
            int(self._chunk_size / int(self._chunk_size / self._CHUNK_SIZE))
            if int(self._chunk_size / self._CHUNK_SIZE) > 0
            else int(self._chunk_size)
        )
        self._chunks_details = {}
        self._tasks = []

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._prepare_queries())
        result = loop.run_until_complete(self._upload_chunks())
        loop.run_until_complete(asyncio.sleep(0.250))
        loop.close()
        return result

    async def _prepare_queries(self):
        start = 0
        async with aiofiles.open(self._file_path, "rb") as file:
            while start < self._file_size - 1:
                end = (
                    self._file_size - 1
                    if start + self._chunk_size > self._file_size - 1
                    else start + self._chunk_size - 1
                )
                size = min(self._chunk_size, end - start + 1)
                data = await self._get_file_chunk(file, size, start)
                headers = {
                    **self._headers,
                    **{
                        "Accept": "*/*",
                        "Content-Type": "application/octet-stream",
                        "Content-Disposition": 'attachment; filename="'
                        + os.path.basename(self._file_path)
                        + '"',
                        "Content-Range": "bytes {}-{}/{}".format(
                            start, end, self._file_size
                        ),
                    },
                }

                self._chunks_details[start] = {
                    "size": size,
                    "data": data,
                    "headers": headers,
                    "ended": False,
                }
                start += self._chunk_size

    async def _upload_chunks(self):
        timeout = aiohttp.ClientTimeout(total=self._QUERY_TIMEOUT)
        conn = aiohttp.TCPConnector(limit=self._workers)
        trace_config = aiohttp.TraceConfig()

        if self._progress:
            trace_config.on_response_chunk_received.append(
                self._on_response_chunk_received
            )
            self._progress(0, self._file_size)

        async with aiohttp.ClientSession(
            timeout=timeout, connector=conn, trace_configs=[trace_config]
        ) as session:
            for uid in self._chunks_details:
                self._tasks.append(
                    asyncio.ensure_future(self._post_chunk(session, self._url, uid))
                )

            try:
                for r in await asyncio.gather(*self._tasks, return_exceptions=False):
                    if r["status"] == 200:
                        return r["content"]
                    if 'content' in r and 'error' in r['content']:
                        raise DailymotionXuploadError(r['content']['error'])
                raise DailymotionXuploadError("Something went wrong.")
            except Exception as e:
                raise DailymotionXuploadError(e)

    async def _on_response_chunk_received(self, session, trace_config_ctx, params):
        uid = trace_config_ctx.trace_request_ctx["uid"]
        self._chunks_details[uid]["ended"] = True
        current = 0

        for req in self._chunks_details:
            if self._chunks_details[req]["ended"]:
                current += self._chunks_details[req]["size"]

        self._progress(current, self._file_size)

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

    async def _post_chunk(self, session, url, chunk_id):
        async with session.post(
            url,
            data=self._chunks_details[chunk_id]["data"],
            headers=self._chunks_details[chunk_id]["headers"],
            proxy=self.PROXY_SOCKET,
            trace_request_ctx={"uid": chunk_id},
            expect100=True,
        ) as resp:
            return {
                "status": resp.status,
                "headers": resp.headers,
                "content": await resp.json(),
                "request_info": resp.request_info,
            }

    async def _get_file_chunk(self, file, chunk_length, chunk_start=0):
        file.seek(chunk_start)
        return await file.read(chunk_length)


class DailymotionXuploadError(Exception):
    pass
