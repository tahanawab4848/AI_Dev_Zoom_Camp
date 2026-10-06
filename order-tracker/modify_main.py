import re

with open('app/main.py', 'r') as f:
    content = f.read()

imports = '''
import logging
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

request_counter = meter.create_counter(
    "request_counts",
    description="Number of requests",
)
'''

content = content.replace('from pydantic import BaseModel, Field\n', 'from pydantic import BaseModel, Field\n' + imports + '\n')

old_get_order = '''@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    with connect() as db:
        row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Order not found")
    return order_detail(row)'''

new_get_order = '''@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    route = "/api/orders/{order_id}"
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("order_id", order_id)
        logger.info(f"Looking up order {order_id}")
        with connect() as db:
            row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        
        if row is None:
            request_counter.add(1, {"route": route, "http_status_code": 404})
            logger.warning(f"Order {order_id} not found")
            raise HTTPException(404, "Order not found")
        
        request_counter.add(1, {"route": route, "http_status_code": 200})
        logger.info(f"Found order {order_id}")
        return order_detail(row)'''

content = content.replace(old_get_order, new_get_order)

old_date_math = 'estimated_at = placed_at.replace(day=placed_at.day + 2)'
new_date_math = 'estimated_at = placed_at + timedelta(days=2)'
content = content.replace(old_date_math, new_date_math)

old_lifespan = '''@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield'''

new_lifespan = '''@asynccontextmanager
async def lifespan(_app: FastAPI):
    FastAPIInstrumentor.instrument_app(_app)
    SQLite3Instrumentor().instrument()
    init_db()
    yield'''

content = content.replace(old_lifespan, new_lifespan)

with open('app/main.py', 'w') as f:
    f.write(content)
