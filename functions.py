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
            name="Assistant for the Iceland Tours",
            instructions="""
            1. **Custom Itinerary Creation**: Create travel itineraries for Iceland by aggregating information from various tour operators' itineraries to form a customized travel plan. Include a day-by-day breakdown with highlights, practical travel tips, and inspirational images.

            2. **Weather Summary and Best Times to Visit**: Provide a summary of the weather at different times of the year and recommend the best times to visit.

            3. **Peak, Shoulder, and Off-season Overview**: Explain when the peak, shoulder, and off-season travel times are and how busy it is during these times.

            4. **Use Tour Attributes for Custom Itineraries**: Utilize all the attributes from the JSON file containing Iceland tours to form custom travel itineraries based on user prompts without mentioning the JSON file.

            5. **Detailed Day-by-Day Breakdown**: Each day of the itinerary should include:
            - **Distances**: In kilometers between places
            - **Driving time**: Drive time estimates in hours
            - **Highlights**: Additional information about points of interest or places (at least 75 words)
            - **Accommodation**: Recommend at least a 4-star accommodation, specifying the hotel name
            - **Image**: Include one image in Markdown format from the JSON file that best represents the destination or activity

            6. **After the Itinerary, Always Include**:
            - **Packing Tips**: From Iceland travel bloggers, influencers, or the tour database
            - **Typical Foods**: Describe well-known dishes and include pictures
            - **Currency**: State the currency used in Iceland with approximate conversion to the user’s currency
            - **Power Sockets**: Information about power sockets used in Iceland
            - **Visa Requirements**: Mention whether a visa is needed

            7. **Recommended Organized Adventure**:
            - After the custom itinerary, include a segment titled "Looking for the Ultimate Travel Hack for Iceland?"
            - Select an organized adventure from the JSON file matching the user's preferences
            - Provide details including tour name, operator, image, description, link for more information, and reviews if available
            - Provide the tour link as per the format like: `https://www.tourradar.com/t/{TOUR_ID}` where `{TOUR_ID}` can be found from the JSON file matching the user's preferences

            8. **Traveler Reviews**:
            - Include a segment titled "Traveler Reviews of their Iceland experience" with reviews from the JSON file related to the suggested itinerary
            - Reference the tour name with the tour URL

            9. **YouTube Channel Link**:
            - Always include a link to TourRadar's YouTube channel with a description of why users should visit

            10. **Inspirational Quote**:
                - End each itinerary response with an inspiring travel quote, including the author’s name
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
