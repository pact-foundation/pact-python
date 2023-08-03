"""The Python implementation of the GRPC AreaCalculator server."""

from concurrent import futures
import logging

import grpc
import area_calculator_pb2
import area_calculator_pb2_grpc

class AreaCalculator(area_calculator_pb2_grpc.CalculatorServicer):

    def calculateOne(self, request, context):
        print(request.rectangle)
        area = request.rectangle.length * request.rectangle.width
        return area_calculator_pb2.AreaResponse(value=[area])


def serve():
    port = '37757'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    area_calculator_pb2_grpc.add_CalculatorServicer_to_server(AreaCalculator(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
