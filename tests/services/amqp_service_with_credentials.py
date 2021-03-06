import asyncio
import os
import signal
import tomodachi
import uuid
from typing import Any
from tomodachi.protocol.json_base import JsonBase
from tomodachi.transport.amqp import amqp, amqp_publish


@tomodachi.service
class AWSSNSSQSService(object):
    name = 'test_amqp'
    log_level = 'INFO'
    message_protocol = JsonBase
    options = {
        'amqp': {
            'login': 'guest',
            'password': 'guest'
        }
    }
    closer = asyncio.Future()  # type: Any
    test_topic_data_received = False
    test_topic_metadata_topic = None
    test_topic_service_uuid = None
    wildcard_topic_data_received = False
    data_uuid = None

    @amqp('test.topic')
    async def test(self, data: Any, metadata: Any, service: Any) -> None:
        if data == self.data_uuid:
            self.test_topic_data_received = True
            self.test_topic_metadata_topic = metadata.get('topic')
            self.test_topic_service_uuid = service.get('uuid')

    @amqp('test.#')
    async def wildcard_topic(self, metadata: Any, data: Any) -> None:
        if data == self.data_uuid:
            self.wildcard_topic_data_received = True

    async def _started_service(self) -> None:
        async def publish(data: Any, routing_key: str) -> None:
            await amqp_publish(self, data, routing_key=routing_key, wait=False)

        async def _async() -> None:
            async def sleep_and_kill() -> None:
                await asyncio.sleep(10.0)
                if not self.closer.done():
                    self.closer.set_result(None)

            asyncio.ensure_future(sleep_and_kill())
            await self.closer
            os.kill(os.getpid(), signal.SIGINT)
        asyncio.ensure_future(_async())

        self.data_uuid = str(uuid.uuid4())
        await publish(self.data_uuid, 'test.topic')

    def stop_service(self) -> None:
        if not self.closer.done():
            self.closer.set_result(None)
