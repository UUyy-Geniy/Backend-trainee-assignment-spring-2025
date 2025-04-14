import asyncio
import logging

from core.engine import get_connection
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import aio as grpc_aio
from grpc_reflection.v1alpha import reflection
from grpc_service.pvz_pb2 import DESCRIPTOR, PVZ, GetPVZListResponse
from grpc_service.pvz_pb2_grpc import (
    PVZServiceServicer,
    add_PVZServiceServicer_to_server,
)
from repository.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncConnection


class PVZServiceServicer(PVZServiceServicer):
    async def GetPVZList(self, request, context):
        conn: AsyncConnection = await get_connection()
        try:
            uow = UnitOfWork(conn)
            async with uow.atomic():
                pvz_list = await uow.pvz.get_all_pvz()

            pvzs = []
            for item in pvz_list:

                ts = Timestamp()
                ts.FromDatetime(item["registration_date"])

                pvzs.append(PVZ(id=str(item["id"]), registration_date=ts, city=item["city"]))
            return GetPVZListResponse(pvzs=pvzs)
        finally:
            await conn.close()


async def serve():
    server = grpc_aio.server()
    add_PVZServiceServicer_to_server(PVZServiceServicer(), server)
    SERVICE_NAMES = (
        DESCRIPTOR.services_by_name["PVZService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    listen_addr = "[::]:3000"
    server.add_insecure_port(listen_addr)
    logging.info(f"gRPC-сервер для PVZ запущен на {listen_addr}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
