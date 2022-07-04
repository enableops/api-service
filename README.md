# enableOps API service

[![Container image](https://github.com/enableops/api-service/actions/workflows/container-image.yaml/badge.svg)](https://github.com/enableops/api-service/actions/workflows/container-image.yaml) [![Tests](https://github.com/enableops/api-service/actions/workflows/tests.yaml/badge.svg)](https://github.com/enableops/api-service/actions/workflows/tests.yaml)

## Schema

- OpenAPI v3 (for Postman) ([prod](https://api.enableops.io/v1/openapi.json))
- Swagger UI ([prod](https://api.enableops.io/docs))
- ReDoc UI ([prod](https://api.enableops.io/redoc))

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
