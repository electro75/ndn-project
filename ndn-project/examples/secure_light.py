import asyncio
import logging
import os
import random
import sys
import tcdicn
import ssl


async def sensor_main(sensor_name, client):
    if sensor_name == "TemperatureSensor":
        tag = "temperature"
        value_range = [0, 30]  
    elif sensor_name == "IntensitySensor":
        tag = "intensity"
        value_range = [0, 100]  
    elif sensor_name == "TouchSensor":
        tag = "Touch"
        value_range = [0, 1] 
    elif sensor_name == "AmbianceSensor":
        tag = "Ambiance"
        value_range = [0, 100]  
    elif sensor_name == "ToneSensor":
        tag = "Tone"
        value_range = [0, 256] 
    else:
        raise ValueError(f"Unknown sensor type: {sensor_name}")

    async def run_sensor():
        while True:
            await asyncio.sleep(random.uniform(1, 2))
            if sensor_name in ["TouchSensor", "TemperatureSensor", "ToneSensor"]:
                value = random.choice(value_range)
            elif sensor_name in ["IntensitySensor", "AmbianceSensor"]:
                value = random.uniform(*value_range)
            logging.info(f"{sensor_name} - Publishing {tag}={value}...")
            try:
                await client.set(tag, value)
            except OSError as e:
                logging.error(f"{sensor_name} - Failed to publish: {e}")

    logging.info(f"{sensor_name} - Starting sensor...")
    sensor = run_sensor()

    both_tasks = asyncio.gather(client.task, sensor)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info(f"{sensor_name} - Client has shutdown.")

async def run_actuator(client, intensity_tag, brightness_tag):
    brightness = 0  # Initial brightness level

    while True:
        # Read intensity value from the IntensitySensor
        intensity = await client.get(intensity_tag)

        # Adjust brightness based on intensity value (example logic)
        if intensity is not None:
            brightness = min(intensity, 100)  # Limit brightness to 100
            logging.info(f"Brightness Actuator - Adjusting brightness to {brightness} based on intensity {intensity}")

        # Set the brightness value
        try:
            await client.set(brightness_tag, brightness)
        except OSError as e:
            logging.error(f"Brightness Actuator - Failed to set brightness: {e}")

        # Sleep for a random interval before checking intensity again
        await asyncio.sleep(random.uniform(1, 2))
async def actuator_main(actuator_name, client, intensity_tag, brightness_tag):
    actuator = run_actuator(client, intensity_tag, brightness_tag)
    logging.info(f"{actuator_name} - Starting actuator...")

    # Define the parameters for the get method
    get_ttl = int(os.environ.get("TCDICN_GET_TTL", 180))
    get_tpf = int(os.environ.get("TCDICN_GET_TPF", 3))
    get_ttp = float(os.environ.get("TCDICN_GET_TTP", 0))

    while True:
        # Read intensity value from the IntensitySensor
        intensity = await client.get(intensity_tag, get_ttl, get_tpf, get_ttp)

        # Adjust brightness based on intensity value (example logic)
        if intensity is not None:
            brightness = min(intensity, 100)  # Limit brightness to 100
            logging.info(f"Brightness Actuator - Adjusting brightness to {brightness} based on intensity {intensity}")
        # Set the brightness value
        try:
            await client.set(brightness_tag, brightness)
        except OSError as e:
            logging.error(f"Brightness Actuator - Failed to set brightness: {e}")

        # Sleep for a random interval before checking intensity again
        await asyncio.sleep(random.uniform(1, 2))

async def main():
    id = os.environ.get("TCDICN_ID")
    port = int(os.environ.get("TCDICN_PORT", random.randint(33334, 65536)))
    server_host = os.environ.get("TCDICN_SERVER_HOST", "localhost")
    server_port = int(os.environ.get("TCDICN_SERVER_PORT", 33333))
    net_ttl = int(os.environ.get("TCDICN_NET_TTL", 180))
    net_tpf = int(os.environ.get("TCDICN_NET_TPF", 3))
    net_ttp = float(os.environ.get("TCDICN_NET_TTP", 0))
    get_ttl = int(os.environ.get("TCDICN_GET_TTL", 180))
    get_tpf = int(os.environ.get("TCDICN_GET_TPF", 3))
    get_ttp = float(os.environ.get("TCDICN_GET_TTP", 0))

    # SSL/TLS context setup
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_cert_chain(certfile='keys/server.crt', keyfile='keys/server.key')

  # Pass the SSL context to the client

    if id is None:
        sys.exit("Please give your client a unique ID by setting TCDICN_ID")

    logging.basicConfig(
        format="%(asctime)s.%(msecs)04d [%(levelname)s] %(message)s",
        level=logging.INFO, datefmt="%H:%M:%S:%m")
    
    # Log SSL/TLS setup
    logging.info("Setting up SSL/TLS context...")
    try:
        ssl_context.check_hostname = False  # If you're using self-signed certificates
        ssl_context.verify_mode = ssl.CERT_NONE  # If you're using self-signed certificates
        logging.info("SSL/TLS context setup completed successfully.")
    except ssl.SSLError as e:
        logging.error(f"SSL/TLS setup failed: {e}")
        return

    logging.info("Starting client...")
   # Start the client with SSL/TLS enabled
    logging.info("Starting client with SSL/TLS...")
    client = tcdicn.Client(
        id, port, ["always"],
        server_host, server_port,
        net_ttl, net_tpf, net_ttp,
        ssl_context=ssl_context
) 
    asyncio.create_task(sensor_main("TemperatureSensor", client))
    asyncio.create_task(sensor_main("IntensitySensor", client))
    asyncio.create_task(sensor_main("TouchSensor", client))
    asyncio.create_task(sensor_main("AmbianceSensor", client))
    asyncio.create_task(sensor_main("ToneSensor", client))

    asyncio.create_task(sensor_main("IntensitySensor", client))
    asyncio.create_task(actuator_main("BrightnessActuator", client, "intensity", "brightness"))

    try:
        await client.task
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())