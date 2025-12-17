# First, you'll need to install the library.
# You can do this from your terminal or command prompt with the following command:
# pip install builtwith

import builtwith
import sys
import json

def get_website_technologies(url: str) -> dict:
    """
    Identifies the web technologies used on a given URL and returns the result
    in a structured dictionary format.

    This function uses the 'builtwith' library to scan a website. It then
    formats the output to include a 'status', 'details', and 'recommendation',
    providing a clear and consistent result for every check.

    Args:
        url (str): The URL of the website to check. Must be a valid URL
                   (e.g., 'https://www.example.com').

    Returns:
        dict: A dictionary containing the check result. It has the following keys:
              - 'status' (str): "pass" on success, "fail" on error.
              - 'details' (str): The technology report as a JSON string on
                                 success, or an error message on failure.
              - 'recommendation' (str): A message suggesting next steps.
    """
    if not url.startswith('http'):
        return {
            "status": "fail",
            "details": f"The URL '{url}' is not valid. Please include the protocol (e.g., 'https://').",
            "recommendation": "Correct the URL to include a protocol (http:// or https://)."
        }
    
    try:
        # builtwith.builtwith() returns a dictionary, which is an unhashable type.
        # We need to convert it to a hashable type, like a string, to prevent errors.
        technologies = builtwith.builtwith(url)
        
        # Convert the technologies dictionary to a JSON-formatted string.
        # This makes it a hashable type that can be safely used in other dictionaries.
        technologies_json_string = json.dumps(technologies, indent=4)
        
        return {
            "status": "pass",
            "details": technologies_json_string,
            "recommendation": "Technology detection successful. Review the 'details' for the report."
        }
    except Exception as e:
        # This can catch various errors, such as network issues, timeouts, or
        # problems with the library itself.
        return {
            "status": "fail",
            "details": f"An error occurred while checking the website: {e}",
            "recommendation": "Check the URL for typos, verify your network connection, or try again later."
        }

