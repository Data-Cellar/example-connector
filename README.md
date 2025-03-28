# Data Cellar Example Data Transfer

This repository contains a simple example of how to:

* Deploy a Data Cellar connector that exposes the API endpoints of an HTTP API in the backend—the data from this API is randomly generated and does not pose any privacy concerns.
* Run an example data transfer where this connector acts as a consumer of another counterparty's Data Cellar provider connector.

## Public Demo Connector

> [!NOTE]  
> The public demo of the connector has been taken down following the completion of System Use Case (SUC) tests in the energy data spaces cluster. If you need a Data Cellar connector for testing, you can deploy this repository on your own infrastructure or contact us, and we’ll do our best to provide access.

This deployment is publicly available at the following endpoints for testing and demonstration purposes in the context of interoperability efforts between the energy data spaces sister projects.

> [!TIP]
> The connector endpoints are exposed both via HTTP, with each API (e.g., Protocol, Management) on a different port, and via a Caddy proxy that terminates the SSL connection, as seen in the `Caddyfile` in this repository.

| Endpoint | URL |
|----------------------------|---------------------------------------------------------------|
| Management API             | `http://dcserver.fundacionctic.org:19193/management` |
| Management API (SSL)       | `https://dcserver.fundacionctic.org/management` |
| Protocol API               | `http://dcserver.fundacionctic.org:19194/protocol` |
| Protocol API (SSL)         | `https://dcserver.fundacionctic.org/protocol` |
| Public API                 | `http://dcserver.fundacionctic.org:19195/public` |
| Public API (SSL)           | `https://dcserver.fundacionctic.org/public` |
| Control API                | `http://dcserver.fundacionctic.org:19192/control` |
| Control API (SSL)          | `https://dcserver.fundacionctic.org/control` |

The IDs of this public demo connector are the following:

```properties
edc.participant.id=datacellar-example-provider
edc.ids.id=datacellar-example-provider
```

## Prerequisites

- **Docker and Docker Compose**: Required to run the connector and its dependencies
- **Python 3.x**: Required for running the example script
- **`openssl`**: Required for certificate generation
- **Task**: A task runner tool ([Taskfile.dev](https://taskfile.dev)) used to manage project commands
- **`envsubst`**: Command-line tool for environment variable substitution

## Configuration

The repository includes an `.env.default` file containing default configuration values. You can override these values by creating a `.env` file in the root directory. In most cases, you'll only need to modify the `PARTICIPANT_HOSTNAME` variable to match your local machine's hostname. Before proceeding, please review the default port numbers in `.env.default` to ensure they don't conflict with other services on your system.

After creating your `.env` file with the appropriate configuration, you can proceed to deploy the connector services and run the data transfer example script.

## Usage

First, deploy the connector services using the provided Docker Compose file by running:

```bash
task connector
```

This command sets up a complete Data Cellar consumer connector environment by performing several steps:

1. It generates the necessary certificates and keystore for the connector.
2. It deploys an HTTP API that generates random values to simulate a mock data source
3. It creates configuration files by substituting environment variables in the templates.
4. It launches three Docker containers: the main EDC connector service, a _consumer backend_ service, and a RabbitMQ message broker.

> [!NOTE]
> The _consumer backend_ service is an HTTP server that receives the `EndpointDataReference` from the provider connector. [See the EDC samples repository for more information](https://github.com/eclipse-edc/Samples/blob/90c18cb9c1a0ecc09a6df273ce961f234a3c6153/transfer/transfer-02-consumer-pull/README.md).

> [!NOTE]
> The RabbitMQ message broker is a custom design decision of the Data Cellar connector. It decouples message handling by allowing the consumer backend to receive messages from the counterparty and process them asynchronously through the message queue.

Then, run the example script to transfer data from the provider connector to the consumer connector:

```bash
task example
```

> [!TIP]
> Please note that the example script executed by the `example` task is available in [`example/example-pull.py`](example/example-pull.py). Also, note that the Protocol URL and connector ID of the counterparty are hardcoded at the top of the file to the values of the public demo connector.

This will create a Python virtual environment and install the `edcpy` dependency, which is a client library developed by Data Cellar to simplify interactions with the Management API of the EDC connector. While not strictly necessary (you can always send requests directly to the Management API), `edcpy` provides a convenient way to interact with the connector.

Then, the script executes a complete data transfer flow by running `example-pull.py`: it negotiates with the provider connector, initiates a transfer request, and pulls data from the provider's API endpoint. The script outputs detailed logs showing each step of the negotiation, transfer, and data retrieval process.

When you've finished, you can remove everything by running:

```bash
task clean
```
