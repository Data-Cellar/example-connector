import asyncio
import logging
import os
import pprint

import coloredlogs
import environ
import httpx
from edcpy.config import AppConfig
from edcpy.edc_api import ConnectorController
from edcpy.messaging import HttpPullMessage, with_messaging_app

_logger = logging.getLogger(__name__)


async def pull_handler(message: dict, queue: asyncio.Queue):
    """Put an HTTP Pull message received from the Rabbit broker into a queue."""

    # Using type hints for the message argument seems to break in Python 3.8.
    message = HttpPullMessage(**message)

    _logger.info(
        "Putting HTTP Pull request into the queue:\n%s", pprint.pformat(message.dict())
    )

    # Using a queue is not strictly necessary.
    # We just need an asyncio-compatible way to pass
    # the messages from the broker to the main function.
    await queue.put(message)


async def request_get(
    counter_party_protocol_url: str,
    counter_party_connector_id: str,
    asset_query: str,
    controller: ConnectorController,
    queue: asyncio.Queue,
    queue_timeout_seconds: int = 30,
):
    """Demonstration of a GET request to the Mock HTTP API."""

    transfer_details = await controller.run_negotiation_flow(
        counter_party_protocol_url=counter_party_protocol_url,
        counter_party_connector_id=counter_party_connector_id,
        asset_query=asset_query,
    )

    transfer_process_id = await controller.run_transfer_flow(
        transfer_details=transfer_details, is_provider_push=False
    )

    http_pull_msg = await asyncio.wait_for(queue.get(), timeout=queue_timeout_seconds)

    if http_pull_msg.id != transfer_process_id:
        raise RuntimeError(
            "The ID of the Transfer Process does not match the ID of the HTTP Pull message"
        )

    async with httpx.AsyncClient() as client:
        _logger.info(
            "Sending HTTP GET request with arguments:\n%s",
            pprint.pformat(http_pull_msg.request_args),
        )

        resp = await client.request(**http_pull_msg.request_args)
        _logger.info("Response:\n%s", pprint.pformat(resp.json()))


async def main(
    counter_party_protocol_url: str,
    counter_party_connector_id: str,
    asset_query: str,
):
    queue: asyncio.Queue[HttpPullMessage] = asyncio.Queue()

    async def pull_handler_partial(message: dict):
        await pull_handler(message=message, queue=queue)

    # Start the Rabbit broker and set the handler for the HTTP pull messages
    # (EndpointDataReference) received on the Consumer Backend from the Provider.
    async with with_messaging_app(http_pull_handler=pull_handler_partial):
        controller = ConnectorController()

        await request_get(
            counter_party_protocol_url=counter_party_protocol_url,
            counter_party_connector_id=counter_party_connector_id,
            asset_query=asset_query,
            controller=controller,
            queue=queue,
        )


if __name__ == "__main__":
    coloredlogs.install(level="DEBUG")

    asyncio.run(
        main(
            counter_party_protocol_url="http://dcserver.fundacionctic.org:19194/protocol",
            counter_party_connector_id="datacellar-example-provider",
            asset_query="GET-consumption",
        )
    )
