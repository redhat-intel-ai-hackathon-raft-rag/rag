import qdrant_client
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.core import Settings
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from rag.data_loader import load_json_nodes, load_raw_documents
from rag.response_synthesizer import response_synthesize


embed_model = FastEmbedEmbedding("BAAI/bge-base-en")
Settings.embed_model = embed_model


class VectorStore:
    index = VectorStoreIndex

    def __init__(self, nodes=None):
        # if nodes is None:
        #     raise ValueError("nodes must be provided")
        self.vector_store = QdrantVectorStore(
            client=qdrant_client.QdrantClient(
                host="localhost",
                port=6333
            ),
            collection_name="webpages",
            prefer_grpc=True
        )

    def load_raw_documents(self, input_dir: str):
        documents = load_raw_documents(input_dir)
        self.index = VectorStoreIndex.from_documents(
            documents=documents,
            storage_context=StorageContext.from_defaults(
                vector_store=self.vector_store,
            )
        )

    def load_json_documents(self, input_dir: str, text_field: str):
        nodes = load_json_nodes(input_dir, text_field)
        self.index = VectorStoreIndex(
                nodes=nodes,
                storage_context=StorageContext.from_defaults(
                    vector_store=self.vector_store,
                )
            )

    def insert(self, document):
        self.index.insert(document)

    def add_nodes(self, nodes):
        """
        examples:
        nodes = [
            TextNode(
                id_="919ea626-2850-4bd9-824f-26689a0d164a",
                text="The author grew up in a large town."
            ),
            TextNode(
                id_="15d6ed4e-bc13-44eb-a1d3-d32baf56d70b",
                text="The author went to college in the city."
            ),
        ]
        """
        self.index.insert_nodes(nodes)

    def get_retriever(self, top_k=3):
        return self.index.as_retriever(
            similarity_top_k=top_k,
        )

    def retrieve(self, text: str, top_k=3):
        """
        retrieving nodes from vector store
        """
        retriver = self.get_retriever(top_k)
        return retriver.retrieve(text)

    def delete_nodes(self, node_ids):
        """
        examples:
        node_ids = ["919ea626-2850-4bd9-824f-26689a0d164a",
                    "15d6ed4e-bc13-44eb-a1d3-d32baf56d70b"]
        """
        self.index.delete_nodes(node_ids)

    def query(self, query: VectorStoreQuery):
        return self.vector_store.query(query)

    def get_index(self):
        return self.index


if __name__ == '__main__':
    # from llm_models import embedding
    nodes = [
        TextNode(
            id_="919ea626-2850-4bd9-824f-26689a0d164a",
            text="The author grew up in a large town."),
        TextNode(
            id_="15d6ed4e-bc13-44eb-a1d3-d32baf56d70b",
            text="The author went to college in the city.")
    ]
    vector_store = VectorStore(nodes)
    nodes = [
        TextNode(
            id_="6d5b9b48-1b38-4e41-bac5-031794bbbaaa",
            text="The author worked at a local restaurant."
        ),
    ]
    vector_store.add_nodes(nodes)
    nodes = vector_store.retrieve("Where did the author grow up?")
    print(nodes)
    print(response_synthesize("Where did the author grow up?", nodes))
