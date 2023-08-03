"""The Python implementation of the GRPC Area Calculator client."""

from __future__ import print_function
import argparse
import logging
import grpc
import area_calculator_pb2
import area_calculator_pb2_grpc

def run(port=37757):
    get_rectangle_area(f'localhost:{port}')

def get_rectangle_area(address):
    print("Getting rectangle area.")
    with grpc.insecure_channel(address) as channel:
        stub = area_calculator_pb2_grpc.CalculatorStub(channel)
        rect = {
            "length": 3,
            "width": 4
        }
        response = stub.calculateOne(area_calculator_pb2.ShapeMessage(rectangle=rect))
    print(f"AreaCalculator client received: {response.value[0]}")
    return response.value[0]


if __name__ == '__main__':
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-p', '--port', help='Port_number', required=False, default=37757)
    args = vars(parser.parse_args())
    run(port=args['port'])
