#!/bin/bash

if kafka-topics.sh --list --bootstrap-server $BROKER | grep -q "^${TOPIC_NAME}$"; then
  echo "Topic ${TOPIC_NAME} already exists."
else
  kafka-topics.sh --create --topic $TOPIC_NAME --partitions $PARTITIONS --replication-factor 1 --bootstrap-server $BROKER
  echo "Topic ${TOPIC_NAME} created."
fi