import typing

import aioboto3
from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from src.core.logger import get_logger


logger = get_logger('api.s3_stream_response')


class S3Stream(StreamingResponse):
    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: BackgroundTask = None,
        key: str = None, bucket: str = None,
        s3_session: aioboto3.Session = None,
        s3_end_point_url: str = None
    ) -> None:
        super(S3Stream, self).__init__(content, status_code, headers, media_type, background)
        self.key = key
        self.bucket = bucket
        self.s3_session = s3_session
        self.s3_end_point_url = s3_end_point_url

    async def stream_response(self, send) -> None:
        async with self.s3_session.client(
                service_name='s3',
                endpoint_url=self.s3_end_point_url,
        ) as client:
            try:
                result = await client.get_object(Bucket=self.bucket, Key=self.key)
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    logger.error('there is no compiled strategy in bucket. compile it before download')
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 404,
                            "headers": self.raw_headers,
                        }
                    )
            else:
                await send(
                    {
                        "type": "http.response.start",
                        "status": self.status_code,
                        "headers": self.raw_headers,
                    }
                )
                async for chunk in result["Body"]:
                    if not isinstance(chunk, bytes):
                        chunk = chunk.encode(self.charset)

                    await send({"type": "http.response.body", "body": chunk, "more_body": True})

        await send({"type": "http.response.body", "body": b"", "more_body": False})
