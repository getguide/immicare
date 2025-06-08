from lambda_function import lambda_handler

# Test event
event = {
    "test": "event"
}

# Run the function
result = lambda_handler(event, None)
print("Result:", result) 