import os
# Unused for the time being


class DocumentStore:
    def __init__(self, directory='data/documents'):
        self.directory = directory
        self.documents = self.load_documents()

    def load_documents(self):
        documents = []
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    documents.append(file.read())

        if not documents:
            print("Warning: No documents found in the directory.")
        else:
            print(f"{len(documents)} documents loaded.")

        return documents
