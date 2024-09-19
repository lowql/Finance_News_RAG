from tests.utils import fetch_documents

def test_dataset_metadata():
    documents = fetch_documents()
    print(f"len of documents is : {len(documents)}")

if __name__  == "__main__":
    test_dataset_metadata()