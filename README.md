# Homemade stupid simple fake dyndns

The purpose of this is to enable knowing what the public IP address is of a
raspberry pi sitting on a home network. It works in two parts. The client
simply sends a PUT request to the server. The server, upon receiving this
PUT request, takes note of the client's IP address and serves this up with GET
requests.

