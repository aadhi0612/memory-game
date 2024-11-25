# Generate cards


import boto3
import json
import base64
import uuid
import random
from io import BytesIO
from datetime import datetime

def generate_image(prompt):
    """
    Generates an image using Titan Image Generator via Amazon Bedrock.
    :param prompt: Text prompt for image generation.
    :return: Base64 encoded image data.
    """
    try:
        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        request_body = {
            "textToImageParams": {
                "text": prompt,
                "width": 512,
                "height": 512,
                "numberOfImages": 1,
                "cfgScale": 8.0,
                "seed": random.randint(0, 100000)
            },
            "taskType": "TEXT_IMAGE",
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "width": 512,
                "height": 512
            }
        }

        response = client.invoke_model(
            modelId="amazon.titan-image-generator-v1",
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response['body'].read())
        
        if 'images' in response_body and response_body['images']:
            return response_body['images'][0]
        return None

    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def upload_to_s3(base64_image, theme):
    """
    Uploads a base64 encoded image to S3.
    :param base64_image: Base64 encoded image data.
    :param theme: Theme name for the card.
    :return: URL of the uploaded image.
    """
    try:
        s3_client = boto3.client('s3')
        
        # Decode base64 image
        image_data = base64.b64decode(base64_image)
        
        # Generate a clean filename
        filename = f"memory-game/{theme.replace(' ', '_')}.png"
        
        # Upload to S3
        s3_client.put_object(
            Bucket="memory-game-bedrock",
            Key=filename,
            Body=image_data,
            ContentType='image/png',
            ACL='public-read'
        )
        
        return f"https://memory-game-bedrock.s3.amazonaws.com/{filename}"
    
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('memory-game-state')
        
        if action == 'start_game':
            # Create new game session
            game_id = str(uuid.uuid4())
            cards = body.get('cards', [])
            
            item = {
                'game_id': game_id,
                'cards': cards,
                'moves': 0,
                'matched_pairs': 0,
                'status': 'in_progress',
                'start_time': int(datetime.now().timestamp()),
                'last_updated': int(datetime.now().timestamp())
            }
            
            table.put_item(Item=item)
            return create_response(200, {
                'game_id': game_id,
                'cards': cards,
                'moves': 0,
                'matched_pairs': 0,
                'status': 'in_progress'
            })
            
        elif action == 'check_match':
            game_id = body.get('game_id')
            card1_id = body.get('card1_id')
            card2_id = body.get('card2_id')
            
            # Get current game state
            response = table.get_item(Key={'game_id': game_id})
            game = response.get('Item')
            
            if not game:
                return create_response(404, {'message': 'Game not found'})
            
            # Find the selected cards
            cards = game['cards']
            card1 = next((card for card in cards if card['id'] == card1_id), None)
            card2 = next((card for card in cards if card['id'] == card2_id), None)
            
            if card1 and card2:
                is_match = card1['theme'] == card2['theme']
                
                # Update cards and game state
                for card in cards:
                    if card['id'] in [card1_id, card2_id]:
                        card['matched'] = is_match
                
                updates = {
                    'cards': cards,
                    'moves': game['moves'] + 1,
                    'matched_pairs': game['matched_pairs'] + (1 if is_match else 0),
                    'last_updated': int(datetime.now().timestamp())
                }
                
                # Check if game is complete
                if updates['matched_pairs'] == len(cards) // 2:
                    updates['status'] = 'completed'
                    updates['end_time'] = int(datetime.now().timestamp())
                
                # Update game state in DynamoDB
                update_expression = 'SET ' + ', '.join(f'#{k} = :{k}' for k in updates.keys())
                expression_attribute_names = {f'#{k}': k for k in updates.keys()}
                expression_attribute_values = {f':{k}': v for k, v in updates.items()}
                
                table.update_item(
                    Key={'game_id': game_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values
                )
                
                return create_response(200, {
                    'is_match': is_match,
                    'game_state': {**game, **updates}
                })
            
            return create_response(400, {'message': 'Invalid card IDs'})
            
        else:
            return create_response(400, {'message': 'Invalid action'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {'error': str(e)})
