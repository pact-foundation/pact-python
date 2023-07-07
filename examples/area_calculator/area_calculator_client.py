"""The Python implementation of the GRPC Area Calculator client."""

from __future__ import print_function

import logging

import grpc
import area_calculator_pb2
import area_calculator_pb2_grpc


def run():
    get_rectangle_area('localhost:37757')

def get_rectangle_area(address):
    print("Getting rectangle area.")
    with grpc.insecure_channel(address) as channel:
        stub = area_calculator_pb2_grpc.CalculatorStub(channel)
        rect ={
          "length": 3,
          "width": 4
        }
        response = stub.calculateOne(area_calculator_pb2.ShapeMessage(rectangle=rect))
    print(f"AreaCalculator client received: {response.value[0]}")
    return response.value[0]

if __name__ == '__main__':
    logging.basicConfig()
    run()
