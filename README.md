# Immiwatch Scraper

A Lambda function that monitors the IRCC Program Delivery Updates page and notifies about new updates via Airtable webhook.

## Features

- Scrapes the IRCC Program Delivery Updates page every 15 minutes
- Stores updates in S3 for historical tracking
- Sends notifications to Airtable via webhook when new updates are found
- Automated deployment using GitHub Actions

## Prerequisites

- AWS Account with appropriate permissions
- Airtable webhook URL
- Python 3.9+
- AWS SAM CLI
- GitHub repository

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/getguide/immiwatch.git
   cd immiwatch
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `AWS_REGION`: Your AWS region (e.g., us-east-1)
   - `S3_BUCKET_NAME`: Name for the S3 bucket
   - `AIRTABLE_WEBHOOK_URL`: Your Airtable webhook URL

4. Deploy:
   ```bash
   sam build
   sam deploy --guided --parameter-overrides S3BucketName=${{ secrets.S3_BUCKET_NAME }} AirtableWebhookUrl=${{ secrets.AIRTABLE_WEBHOOK_URL }}
   ```

## Development

- The main Lambda function is in `src/functions/scraper/lambda_function.py`
- Tests are in the `tests/` directory
- Infrastructure is defined in `template.yaml`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
