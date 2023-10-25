import json
import grpc
import logging
import asyncio

from ..ctl.resp import RespDefaultSuccess, RespDefaultError
from ..config.config import DEFAULT_MILVUS_TABLE_NAME, VECTOR_ADDR, ETCD_HOST,ETCD_PORT 
from ..milvus.operators import do_search
from ..etcd_operate.etcd import etcd_client
from ..milvus.milvus import milvus_client
from idl.pb.search_vector import search_vector_pb2_grpc


class SearchVectorService(search_vector_pb2_grpc.SearchVectorServiceServicer):

    def SearchVector(self, request, context):
        try:
            queryies = request.query
            doc_ids = []
            for query in queryies:
                ids, distants = do_search(DEFAULT_MILVUS_TABLE_NAME, query, 1, milvus_client)
                print("search vector ids", ids)
                doc_ids += ids
            print("search vector data", doc_ids)
            return RespDefaultSuccess(doc_ids)
        except Exception as e:
            print("search vector error", e)
            return RespDefaultError(str(e))


async def serve() -> None:
    server = grpc.aio.server()
    search_vector_pb2_grpc.add_SearchVectorServiceServicer_to_server(SearchVectorService(), server)
    # listen_addr = "[::]:50051"
    server.add_insecure_port(VECTOR_ADDR[0])
    logging.info("Starting server on %s", VECTOR_ADDR[0])
    # print("ETCD_HOST,ETCD_PORT", ETCD_HOST, ETCD_PORT)
    key = f"/search_vector/{VECTOR_ADDR}"
    value = json.dumps({"name":"search_vector","addr":f"{VECTOR_ADDR}","version":"","weight":0})
    etcd_client.set(key, value)
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())