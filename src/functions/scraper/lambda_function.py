import json
import os
import boto3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
WEBHOOK_URL = os.environ.get('AIRTABLE_WEBHOOK_URL')

def get_latest_updates():
    """Scrape the IRCC updates page and return the latest updates."""
    url = "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/operational-bulletins-manuals/updates.html"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the updates table
        updates = []
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    update = {
                        'category': cols[0].text.strip(),
                        'title': cols[1].text.strip(),
                        'date': cols[2].text.strip(),
                        'url': cols[1].find('a')['href'] if cols[1].find('a') else None
                    }
                    updates.append(update)
        
        return updates
    except Exception as e:
        logger.error(f"Error scraping updates: {str(e)}")
        raise

def save_to_s3(updates):
    """Save the updates to S3."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f'updates/{timestamp}.json'
    
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(updates),
            ContentType='application/json'
        )
        return key
    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}")
        raise

def notify_airtable(new_updates):
    """Send new updates to Airtable webhook."""
    if not WEBHOOK_URL:
        logger.warning("No Airtable webhook URL configured")
        return
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json={'updates': new_updates},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error notifying Airtable: {str(e)}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler function."""
    try:
        # Get latest updates
        updates = get_latest_updates()
        
        # Save to S3
        s3_key = save_to_s3(updates)
        logger.info(f"Saved updates to S3: {s3_key}")
        
        # Get the last saved state from S3
        try:
            last_state = s3.get_object(
                Bucket=BUCKET_NAME,
                Key='last_state.json'
            )
            last_updates = json.loads(last_state['Body'].read())
        except:
            last_updates = []
        
        # Find new updates
        new_updates = [u for u in updates if u not in last_updates]
        
        if new_updates:
            # Notify Airtable about new updates
            notify_airtable(new_updates)
            logger.info(f"Found {len(new_updates)} new updates")
        
        # Update last state
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key='last_state.json',
            Body=json.dumps(updates),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Success',
                'new_updates': len(new_updates)
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 