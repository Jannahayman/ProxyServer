Simple Web Proxy Server in Python

A lightweight and efficient web proxy server implemented in Python. This proxy server intercepts HTTP requests, forwards them to the original server, caches responses, and serves subsequent requests from the cache when possible. The code includes features like URL filtering, content type recognition, and support for various file formats.

Features
1. HTTP Proxy: Intercept and forward HTTP requests and responses.
2. Caching: Cache responses for faster retrieval on subsequent requests.
3. URL Filtering: Block access to forbidden URLs based on a predefined list.
4. Content Type Recognition: Identify and handle various file formats (HTML, images, CSS, JavaScript, etc.).
5. Error Handling: Handle 404 Not Found responses gracefully.
6. User-Agent and Referer Preservation: Preserve original User-Agent and Referer headers in the forwarded request.


Usage:

Clone the Repository

Configure Clients,
Set your clients to use the proxy server by specifying the proxy IP and port.

