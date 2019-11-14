#!/usr/bin/env python3
# -*- coding: utf-8; mode: python -*-

import libcitisim

import pykafka

import argparse
import contextlib
import json
import sys

EPILOG = '''
Forward citisim topics messages to a kafka cluster'''


class KafkaClusterSanitizer(argparse.Action):
    ''' Prepare command line kafka brokers to pykafka '''
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace,
                self.dest,
                KafkaClusterSanitizer._sanitize_kafka_args(values))

    @staticmethod
    def _sanitize_kafka_args(in_str):
        ''' Sanitize kafka brokers and assign default port if it does not
        provide it
        '''
        return ','.join(broker+':9092' if ':' not in broker else broker
                        for broker in in_str.split(','))


class SubscriberArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(**{
            'description': 'Libcitisim kafka mirror',
            'epilog': EPILOG,
            **kwargs})

        self.add_argument('libcitisim_args',
                          nargs='*',
                          default=['kmirror-bidir.config'],
                          help='Libcitisim config file')
        self.add_argument('--kafka-cluster',
                          required=True,
                          metavar='<bootstrap kafka brokers>',
                          action=KafkaClusterSanitizer,
                          help='The kafka cluster to which to connect')
        self.add_argument('--forward-topic',
                          action='append',
                          #default=['Temperature'],
                          help='The kafka topic to forward')


@contextlib.contextmanager
def kafka_mirror_producer(kafka_cluster, topic_name, **topic_kwargs):
    ''' Kafka producer context manager, useful for wait for pending messages in
    producer close '''
    byte_topic_name = topic_name.encode()
    with kafka_cluster.topics[byte_topic_name].get_producer() as producer:
        yield producer


class EventMirrorVisitor:
    ''' libcitisim per-message visitor '''
    def __init__(self, producer):
        self.producer = producer

    def callback(self, value, source, metadata):
        ''' Callback to call for each libcitisim message received '''
        message = {'value': value,
                   'source': source,
                   'meta': {
                        key: value for key, value in metadata.items()
                   }}

        compact_separators = (',', ':')

        payload = json.dumps(message, separators=compact_separators).encode()
        self.producer.produce(payload)


class SubscriberMirror:
    ''' Main class, prepare kafka and citisim broker and connects them '''
    def run(self, libcitisim_config, producers):
        ''' Main function '''
        citisim_broker = libcitisim.Broker(libcitisim_config)

        for topic_name, producer in producers.items():
            print("Subscribing to '{}' topic".format(topic_name))
            citisim_broker.subscribe(topic_name,
                                     EventMirrorVisitor(producer).callback)

        print("Awaiting data...")
        citisim_broker.wait_for_events()


if __name__ == "__main__":
    args = SubscriberArgumentParser().parse_args(sys.argv[1:])

    kafka_events_handler = pykafka.handlers.ThreadingHandler()
    kafka_cluster = pykafka.cluster.Cluster(hosts=args.kafka_cluster,
                                            handler=kafka_events_handler)

    with contextlib.ExitStack() as exit_stack:
        kafka_producers = {topic_name: exit_stack.enter_context(
                                kafka_mirror_producer(kafka_cluster,
                                                      topic_name))
                           for topic_name in args.forward_topic}

        SubscriberMirror().run(
            libcitisim_config=args.libcitisim_args[0],
            producers=kafka_producers)
