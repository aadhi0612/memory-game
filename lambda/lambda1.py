import boto3
import json
import base64
import time
import random
import concurrent.futures

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        # Initialize clients
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        s3 = boto3.client('s3')
        
        # Get number of pairs (default to 2)
        number_of_pairs = int(event.get('number_of_pairs', 2))
        
        # Simple themes with prompts
        theme_prompts = {
            "cat": "cute cartoon cat face, simple illustration, white background, centered, minimalist style",
            "dog": "cute cartoon dog face, simple illustration, white background, centered, minimalist style",
            "bird": "cute cartoon bird face, simple illustration, white background, centered, minimalist style",
            "fish": "cute cartoon fish, simple illustration, white background, centered, minimalist style"
        }
        
        # Select themes based on number_of_pairs
        themes = list(theme_prompts.keys())[:number_of_pairs]
        cards = []
        
        # Calculate remaining time
        time_remaining = context.get_remaining_time_in_millis() / 1000  # Convert to seconds
        print(f"Time remaining: {time_remaining} seconds")

        # Set timeout buffer
        TIMEOUT_BUFFER = 5  # seconds
        MAX_TIME_PER_IMAGE = (time_remaining - TIMEOUT_BUFFER) / len(themes)
        
        for theme in themes:
            try:
                start_time = time.time()
                
                # Check remaining time
                if context.get_remaining_time_in_millis() / 1000 < TIMEOUT_BUFFER:
                    print("Not enough time remaining, stopping processing")
                    break

                request_body = {
                    "textToImageParams": {
                        "text": theme_prompts[theme],
                        "negativeText": "text, words, blurry, distorted, ugly, bad anatomy"
                    },
                    "taskType": "TEXT_IMAGE",
                    "imageGenerationConfig": {
                        "cfgScale": 8,
                        "seed": random.randint(0, 100000),
                        "width": 512,  # Reduced size for faster generation
                        "height": 512,
                        "numberOfImages": 1,
                        "quality": "standard"
                    }
                }

                print(f"Generating image for {theme}")
                response = bedrock.invoke_model(
                    modelId="amazon.titan-image-generator-v1",
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json"
                )
                
                response_body = json.loads(response['body'].read())
                
                if 'images' in response_body:
                    image_data = base64.b64decode(response_body['images'][0])
                    
                    timestamp = int(time.time())
                    key = f"memory-game/{theme}_{timestamp}.png"
                    
                    s3.put_object(
                        Bucket="memory-game-bedrock",
                        Key=key,
                        Body=image_data,
                        ContentType='image/png',
                        ACL='public-read',
                        CacheControl='no-cache'
                    )
                    
                    image_url = f"https://memory-game-bedrock.s3.amazonaws.com/{key}"
                    
                    cards.extend([
                        {
                            "id": f"{theme}_1_{timestamp}",
                            "theme": theme,
                            "image_url": image_url,
                            "matched": False
                        },
                        {
                            "id": f"{theme}_2_{timestamp}",
                            "theme": theme,
                            "image_url": image_url,
                            "matched": False
                        }
                    ])
                    print(f"Successfully generated and saved image for {theme}")
                
                # Calculate time taken and adjust delay
                time_taken = time.time() - start_time
                if time_taken < MAX_TIME_PER_IMAGE:
                    time.sleep(0.5)  # Small delay between requests
            
            except Exception as e:
                print(f"Error processing {theme}: {str(e)}")
                continue
        
        # Shuffle the cards
        random.shuffle(cards)
        
        if not cards:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Failed to generate any cards",
                    "message": "Please try again"
                })
            }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "cards": cards,
                "message": "Cards generated successfully"
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e),
                "message": "An error occurred while processing the request"
            })
        }




