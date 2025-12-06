"""
AWS Lambda handler using Mangum to adapt FastAPI.
"""
from mangum import Mangum
from main_lambda import app

handler = Mangum(app, lifespan="off")
