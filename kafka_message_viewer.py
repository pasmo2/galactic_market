#!/usr/bin/env python
"""
Simple Kafka Message Viewer
Shows raw messages from Kafka topics in a clear format
"""
import json
import subprocess
import sys
import time
from datetime import datetime

def view_kafka_messages(topic, max_messages=None):
    """View messages from a Kafka topic in a readable format"""
    cmd = [
        "docker-compose", "exec", "-T", "kafka", 
        "kafka-console-consumer", 
        "--bootstrap-server", "localhost:9092", 
        "--topic", topic,
        "--from-beginning"
    ]
    
    print(f"Viewing messages from topic: {topic}")
    print("Press Ctrl+C to exit\n")
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        message_count = 0
        while True:
            # Check if we've reached the maximum message count
            if max_messages and message_count >= max_messages:
                break
                
            line = process.stdout.readline().strip()
            if not line:
                time.sleep(0.1)  # Prevent CPU spinning
                continue

            try:
                data = json.loads(line)
                timestamp = data.get('timestamp')
                if timestamp:
                    # Convert Unix timestamp to readable format
                    time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = "Unknown"
                    
                # Extract key information
                demand_id = data.get('demand_id', 'Unknown')
                status = data.get('status', 'Unknown')
                details = data.get('details', {})
                
                # Format output
                print(f"Time: {time_str}")
                print(f"Demand ID: {demand_id}")
                print(f"Status: {status}")
                
                # Show details if they exist
                if details:
                    print("Details:")
                    for key, value in details.items():
                        print(f"  {key}: {value}")
                        
                print("-" * 50)
                
                message_count += 1
                
            except json.JSONDecodeError:
                print(f"Error parsing: {line}")
                
    except KeyboardInterrupt:
        print("\nStopping message viewer...")
    finally:
        if process:
            process.terminate()

if __name__ == "__main__":
    topic = 'demand-status-updates'
    max_messages = None
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        max_messages = int(sys.argv[2])
    
    view_kafka_messages(topic, max_messages) 