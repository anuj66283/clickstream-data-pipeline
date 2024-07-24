from faker import Faker
from fastapi import FastAPI
from faker_clickstream import ClickstreamProvider

fake = Faker()
fake.add_provider(ClickstreamProvider)

app = FastAPI()

@app.get("/{x}")
def clickstream(x: int):
    dat =  fake.session_clickstream(rand_session_max_size=x)
    return dat 
