# enableOps API service

[![Container image](https://github.com/enableops/api/actions/workflows/container-image.yaml/badge.svg)](https://github.com/enableops/api/actions/workflows/container-image.yaml) [![Tests](https://github.com/enableops/api/actions/workflows/tests.yaml/badge.svg)](https://github.com/enableops/api/actions/workflows/tests.yaml)

## Stack

- FastAPI powered
- OpenAPI v3 schema (for Postman) ([prod](https://api.enableops.io/v1/openapi.json)/[dev](https://api-dev.enableops.io/v1/openapi.json))
- Swagger UI ([prod](https://api.enableops.io/docs)/[dev](https://api-dev.enableops.io/docs))
- ReDoc UI ([prod](https://api.enableops.io/redoc)/[dev](https://api-dev.enableops.io/redoc))

## Capabilities

- Auth
  - OAuth2 authorization to Google
  - Settings endpoint
  - Logout endpoint
- Data from Google API
  - Profile info
  - Google Cloud Projects list fetch via Resource Manager API
- enableOps configuration
  - Configuration dispatch
  - Configuration statuses fetch
  - Configuration statuses update

## Details

- Dispatching configuration will start [the workflow of adding new customer](https://github.com/enableops/terraform/actions/workflows/add-customer.yml) to terraform configuration.
- Each status fetch will activate status update for corresponding configuration(s)

## Deployment

- Hosted at GKE as [ArgoCD app](https://github.com/enableops/gitops-enableops-infra/blob/main/outpost/Application-API-outpost.yaml)
- Container image available at https://eu.gcr.io/enableops-io/api

## Environments

- Production: https://api.enableops.io
- ~~ Dev: https://api-dev.enableops.io ~~
