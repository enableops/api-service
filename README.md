# enableOps API service

[![Container image](https://github.com/enableops/api-service/actions/workflows/container-image.yaml/badge.svg)](https://github.com/enableops/api-service/actions/workflows/container-image.yaml) [![Tests](https://github.com/enableops/api-service/actions/workflows/tests.yaml/badge.svg)](https://github.com/enableops/api-service/actions/workflows/tests.yaml)


- [Swagger UI](https://api.enableops.io/docs)
- [ReDoc UI](https://api.enableops.io/redoc)
- [OpenAPI v3 Schema](https://api.enableops.io/v1/openapi.json) (for Postman)


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


## Configuration

**Mandatory**
- `GITHUB` - JSON configuration for triggering infrastructure updates with `token`, `repo_name`, `workflow_file`, `ref` fields
- `API__TERRAFORM_KEY` - key to be used by infrastructure to list/update configured projects list
- `OAUTH__CLIENT_ID` - id to establish oauth using third party service (e.g. Google Accounts)
- `OAUTH__CLIENT_SECRET` - secret to establish oauth using third party service (e.g. Google Accounts)	
- `OAUTH__SCOPES` - scopes that will be requested during oauth session	
- `LITESTREAM_ACCESS_KEY_ID` - key id for accessing db replication s3 bucket
- `LITESTREAM_SECRET_ACCESS_KEY` - key secret for accessing db replication s3 bucket

**Optional**
- `API__CORS` - comma separated list of domains for CORS policy
- `API__SENTRY_DSN`	- url for sending logs to [sentry.io](https://sentry.io/)
- `JWT__TOKEN_EXPIRE_MINUTES` - auth session expiry timeout
- `JWT__ENCRYPTION_KEY` - key to protect/sign user auth data 
- `API__SESSION_KEY` - key to protect/sign user sessions data 
- `CRYPTO_KEY` - key to protect user persistent data 
