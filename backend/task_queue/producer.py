import pika
import json
import os
import structlog

logger = structlog.get_logger()
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

class QueueProducer:
    def __init__(self):
        # In a real async system, use aio_pika, but for simplicity pika is fine for demonstrating
        # We will connect on demand or keep a pool. 
        pass

    def publish_ingestion_job(self, file_path: str, filename: str, tenant_id: str):
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            queue_name = "document_ingestion"
            channel.queue_declare(queue=queue_name, durable=True)
            
            payload = {
                "file_path": file_path,
                "filename": filename,
                "tenant_id": tenant_id
            }
            
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            
            logger.info("job_published", queue=queue_name, filename=filename, tenant_id=tenant_id)
            connection.close()
        except Exception as e:
            logger.error("publish_failed", error=str(e))
            raise

producer = QueueProducer()
