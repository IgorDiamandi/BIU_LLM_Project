import os
import json
import docx
import subprocess
import re

# Load the prompt from prompt.txt
def load_prompt():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    prompt_file = os.path.join(script_directory, "prompt.txt")
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: prompt.txt file not found.")
        return None

# Read and parse DOCX file content
def read_docx_file(filepath):
    doc = docx.Document(filepath)
    # Include all paragraphs in the full text
    full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return full_text

# Enhanced extraction function for structured fields
def extract_fields(document_text):
    extracted_data = {
        "course_name": None,
        "program_manager": "מר ערן שחם, מנהל בית הספר להייטק וסייבר באוניברסיטת בר-אילן",
        "instructors": [],
        "summary": None,
        "embedded_images": [],
        "full_text": document_text  # Include all document text here
    }

    # Extract course name
    course_name_match = re.search(r"מסלול הכשרת\s+(.+)", document_text)
    if course_name_match:
        extracted_data["course_name"] = course_name_match.group(1).strip()

    # Improved instructor extraction
    # This pattern looks for instructor titles and roles, capturing full names and additional information if provided
    instructor_matches = re.findall(r"(מר|עו\"ד|גב')\s+([^\n,]+)(?:,\s*([\w\s]+))?", document_text)
    for match in instructor_matches:
        title, name, role = match
        instructor_data = {
            "name": f"{title} {name}".strip(),
            "role": role if role else "Instructor",  # Default to "Instructor" if role is unspecified
            "title": None,
            "description": None
        }
        extracted_data["instructors"].append(instructor_data)

    # Extract summary based on introductory phrases
    summary_match = re.search(r"(?:תחום הבינה העסקית|המסלול להכשרת).+?(?=\n\n|$)", document_text, re.DOTALL)
    if summary_match:
        extracted_data["summary"] = summary_match.group(0).strip()

    return extracted_data

# Function to call Ollama's Llama model via subprocess
def analyze_document(prompt, document_text):
    # Combine the prompt and document text into a single input
    combined_input = f"{prompt}\n\n{document_text}"

    command = [
        'ollama', 'run', 'llama3.2:latest'
    ]
    try:
        result = subprocess.run(command, input=combined_input, capture_output=True, text=True, encoding='utf-8', check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error with Ollama command: {e.stderr}")
        return None

# Main function to process all DOCX files
def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Load prompt content
    prompt = load_prompt()
    if prompt is None:
        print("Aborting: Unable to load prompt.")
        return

    for filename in os.listdir(current_directory):
        if filename.endswith(".docx"):
            filepath = os.path.join(current_directory, filename)
            print(f"Processing document: {filename}")

            # Extract document text
            document_text = read_docx_file(filepath)

            # Structured data extraction
            extracted_data = extract_fields(document_text)

            # Generate JSON result using Ollama
            result_json = analyze_document(prompt, document_text)
            if result_json:
                try:
                    # Attempt to parse JSON output if it appears valid
                    output_data = json.loads(result_json)
                    extracted_data.update(output_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON for {filename}")

                # Save output to JSON
                output_filename = os.path.splitext(filename)[0] + ".json"
                output_path = os.path.join(current_directory, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=4)
                print(f"Saved JSON output to {output_path}")

if __name__ == "__main__":
    main()
