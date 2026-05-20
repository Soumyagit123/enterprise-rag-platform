import pika
import json
import os
import structlog
import asyncio
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ingestion import ingestion_service
from services.embedding import embedding_service
from services.vector_store import vector_store

logger = structlog.get_logger()
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def process_message(ch, method, properties, body):
    payload = json.loads(body)
    file_path = payload.get("file_path")
    filename = payload.get("filename")
    tenant_id = payload.get("tenant_id")
    
    logger.info("received_job", filename=filename, tenant_id=tenant_id)
    
    try:
        # In a real scenario, download file from S3 or read from shared volume
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
                
            # Run async ingestion service in sync wrapper for pika
            loop = asyncio.get_event_loop()
            child_chunks = loop.run_until_complete(
                ingestion_service.process_document(content, filename, tenant_id)
            )
            
            # Phase 3: Embedding and Vector Storage
            if child_chunks:
                # 1. Embed the child chunks
                embedded_chunks = loop.run_until_complete(
                    embedding_service.generate_embeddings(child_chunks)
                )
                
                # 2. Store in Pinecone (Sync call via Pinecone SDK)
                vector_store.store_chunks(embedded_chunks, tenant_id)
            
            logger.info("job_completed", chunks_stored=len(child_chunks))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logger.error("file_not_found", file_path=file_path)
            # Nack without requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    except Exception as e:
        logger.error("job_failed", error=str(e), exc_info=True)
        # Nack and requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    logger.info("starting_consumer")
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    queue_name = "document_ingestion"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue=queue_name, on_message_callback=process_message)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()

if __name__ == "__main__":
    start_consumer()
