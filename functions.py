import json
import os

from openai import OpenAI

FILE_PATH = "tour_data/iceland_adventures.json"


def create_assistant(client: OpenAI):
    assistant_file_path = "assistant.json"

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, "r") as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data["assistant_id"]
            print("Loaded existing assistant ID.")
    else:
        assistant_file = client.files.create(
            file=open(FILE_PATH, "rb"), purpose="assistants"
        )

        # Create a vector store caled "Financial Statements"
        vector_store = client.beta.vector_stores.create(name="Tour details")

        # Ready the files for upload to OpenAI
        file_paths = [FILE_PATH]
        file_streams = [open(path, "rb") for path in file_paths]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        # You can print the status and the file counts of the batch to see the result of this operation.
        print("File batch status: ", file_batch.status)
        print("Batch file counts: ", file_batch.file_counts)

        assistant = client.beta.assistants.create(
            name="Travel assistant for Iceland adventures",
            instructions="""The travel assistant is responsible for answering travelers' and tour operators' questions based on the provided JSON file with tour details. It must interpret natural language queries to fetch and present accurate information such as itineraries, pricing, availability, and other relevant details. The assistant should ensure user-friendly interaction and handle queries efficiently, providing clear and helpful responses for the tour only for which the data is being provided else provide the error regarding any context out of the file and for which is not relevant for the tour.""",
            model="gpt-4-turbo",
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        with open(assistant_file_path, "w") as file:
            json.dump(
                {
                    "assistant_id": assistant.id,
                    "file_id": assistant_file.id,
                    "vector_store_id": vector_store.id,
                },
                file,
            )
            print("Created a new assistant, file and vector files and saved IDs.")
        assistant_id = assistant.id
    return assistant_id
