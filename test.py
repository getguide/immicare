import lambda_function

# Test event
event = {
    "test": "event"
}

# Run the function
result = lambda_function.lambda_handler(event, None)
print("Result:", result) 