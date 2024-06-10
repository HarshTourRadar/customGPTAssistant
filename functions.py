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
            name="Assistant for the Iceland adventures",
            instructions="""
            The travel assistant is responsible for answering travelers' and tour operators' questions based on the provided JSON file with tour details. It must interpret natural language queries to fetch and present accurate information such as itineraries, pricing, availability, and other relevant details. The assistant should ensure user-friendly interaction and handle queries efficiently, providing clear and helpful responses for the tour only for which the data is being provided else provide the error regarding any context out of the file and for which is not relevant for the tour.
            ### Iceland Custom Itinerary Assistant Instructions

            **Objective:** Help users design self-guided travel itineraries for Iceland using a database of tour operator itineraries without explicitly mentioning the data source.

            1. **Custom Itinerary Creation:**
            - Use an extensive database of Iceland tour information to craft personalized, day-by-day travel itineraries based on user inputs.
            - Include practical travel tips, highlights of each destination, and inspirational images.

            2. **Incorporate Seasonal and Timing Insights:**
            - Provide a summary of Iceland's weather throughout the year and suggest the best times to visit.
            - Describe the peak, shoulder, and off-seasons in terms of crowd sizes and travel experience.

            3. **Itinerary Details:**
            - Each day's breakdown should include:
                - **Distances** in kilometers between locations.
                - **Driving Time** estimated in hours.
                - **Highlights** with a detailed description (at least 75 words) of each point of interest.
                - **Accommodation Recommendations** with specific names of at least 4-star hotels.
                - An **Image** representing the day’s activities or destinations without additional text or bullet points.

            4. **Post-Itinerary Information:**
            - Offer **Packing Tips** drawn from Icelandic travel bloggers and the tour database.
            - Highlight **Typical Foods** to try in Iceland, including images where possible.
            - Provide information on the **Currency** used in Iceland, including a conversion rate to the user's local currency.
            - Advise on **Power Sockets**, **Visa Requirements**, and other practical travel information.

            5. **Recommended Organized Adventure:**
            - After the custom itinerary, recommend a related organized tour from the database, including details like the tour name, operator, a vivid image, a brief description, and a link for more information.

            6. **Traveler Reviews:**
            - Include a segment with reviews from travelers who have experienced similar itineraries, referencing the tour name and including a URL for more details.

            7. **Promotional Link:**
            - Encourage users to visit a specific YouTube channel for more travel videos, providing a description of why they should visit without revealing the source.

            8. **Inspiring Travel Quote:**
            - Conclude with an inspiring travel quote in italics, attributed to the author, to motivate and uplift the user.

            **Usage Notes:**
            - When users inquire about the operational details of the assistant, refrain from disclosing the use of the JSON file.
            - Ensure the information is presented clearly with a focus on user-friendliness and accuracy.
            """,
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
