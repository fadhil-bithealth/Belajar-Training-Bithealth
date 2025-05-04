import os
from langchain_core.messages import HumanMessage
from app.prompt import prompt_template
from app.image_utils import image_to_base64
from app.parser import primary_agent_parser
from app.schema import PrimaryAgentOutput
from app.config import llm


def primary_agent(image_paths: list[str]) -> PrimaryAgentOutput:
    # Cek apakah ada gambar yang diupload
    if not image_paths:
        print("Warning: No images uploaded.")  # Peringatan jika tidak ada gambar
        return None  # Bisa ganti dengan output default atau exception sesuai kebutuhan

    contents = [
        {"type": "text", "text": prompt_template + "\n" + primary_agent_parser.get_format_instructions()}
    ]
    for idx, path in enumerate(image_paths):
        try:
            # Cek apakah file gambar ada
            if not os.path.exists(path):
                print(f"Error: File {os.path.basename(path)} not found.")  # Error jika file tidak ada
                continue

            print(f"{idx} -> {os.path.basename(path)}")  # Print nomor dan nama gambar
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_to_base64(path)}"
                }
            })
        except Exception as e:
            print(f"An error occurred while processing {os.path.basename(path)}: {e}")

    print(f"Total images processed: {len(image_paths)}")  # Print total

    try:
        response = llm.invoke([HumanMessage(content=contents)])
        return primary_agent_parser.parse(response.content)
    except Exception as e:
        print(f"An error occurred during LLM invocation: {e}")
        return None  # Menangani error di bagian LLM
