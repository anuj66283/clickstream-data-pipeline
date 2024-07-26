import os
import json
import aiohttp
import asyncio
from random import randint
from aiokafka import AIOKafkaProducer

URL = os.getenv('URL')
TOPIC = os.getenv('TOPIC_NAME')

def serializer(msg):
    return json.dumps(msg).encode('utf-8')

async def fetch(session, url):
    x = randint(1, 100)
    try:
        async with session.get(url+str(x)) as resp:
            print(f"Getting data from {url+str(x)}")
            resp.raise_for_status()
            return await resp.json()
    except aiohttp.ClientError as e:
        print(f"Error {e}")
        return None

async def main(url, x):
    async with aiohttp.ClientSession() as ses:
        tasks = [fetch(ses, url) for _ in range(x)]
        results = await asyncio.gather(*tasks)
        return results
    
async def send_to_kafka(producer, data):
    await asyncio.sleep(randint(0, 4))
    await producer.send_and_wait(TOPIC, data)

async def produce():
    producer = AIOKafkaProducer(
        bootstrap_servers=[os.getenv('BROKER')],
        value_serializer=serializer
    )

    x = randint(5, 20)

    results = await main(URL, x)
    

    try:
        await producer.start()

        for res in results:
            print("Results")
            send_tasks = []
            for val in res:
                if val:
                    task = asyncio.create_task(send_to_kafka(producer, val))
                    send_tasks.append(task)
            await asyncio.gather(*send_tasks)
    
    except Exception as e:
        print(f"Error sending {e}")
        
    finally:
        await producer.stop()
    

async def main_loop():
    while True:
        await produce()
        await asyncio.sleep(1)

asyncio.run(main_loop())