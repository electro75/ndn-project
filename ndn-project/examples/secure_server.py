import asyncio
import logging
import os
import ssl
import tcdicn

async def main():
    # Get parameters or defaults
    port = int(os.environ.get("TCDICN_PORT", 33333))
    net_ttl = int(os.environ.get("TCDICN_NET_TTL", 180))
    net_tpf = int(os.environ.get("TCDICN_NET_TPF", 3))

    # Logging verbosity
    logging.basicConfig(
        format="%(asctime)s.%(msecs)04d [%(levelname)s] %(message)s",
        level=logging.INFO, datefmt="%H:%M:%S:%m")

    # SSL/TLS context setup
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='keys/server.crt', keyfile='keys/server.key')

    # Start the server as a background task with SSL/TLS enabled
    logging.info("Starting server with SSL/TLS...")
    server = tcdicn.Server(port, net_ttl, net_tpf, ssl_context=ssl_context)

    # Wait for the server to shutdown
    try:
        await server.task
    except asyncio.exceptions.CancelledError:
        logging.info("Server has shutdown.")

if __name__ == "__main__":
    asyncio.run(main())
