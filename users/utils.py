"""
Utility functions for the users app.

Contains custom exception handler for consistent API error responses.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps all error responses in a
    consistent JSON format:
    
    {
        "success": false,
        "error": {
            "code": 400,
            "message": "Human readable error message",
            "details": { ... }  // optional field-level errors
        }
    }
    
    Why? Consistent error formats make it much easier for frontend
    developers to handle errors. They always know the shape of the response.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': _get_error_message(response),
            }
        }
        
        # Include field-level details if available (e.g., validation errors)
        if isinstance(response.data, dict):
            # Filter out the 'detail' key since we already use it as message
            details = {k: v for k, v in response.data.items() if k != 'detail'}
            if details:
                error_data['error']['details'] = details
        
        response.data = error_data
    
    return response


def _get_error_message(response):
    """Extract a human-readable message from the DRF response."""
    if isinstance(response.data, dict) and 'detail' in response.data:
        return str(response.data['detail'])
    if isinstance(response.data, list):
        return str(response.data[0])
    
    # Map status codes to default messages
    messages = {
        400: "Bad request. Please check your input.",
        401: "Authentication required. Please log in.",
        403: "You don't have permission to perform this action.",
        404: "The requested resource was not found.",
        405: "This HTTP method is not allowed for this endpoint.",
        500: "An internal server error occurred.",
    }
    return messages.get(response.status_code, "An error occurred.")
