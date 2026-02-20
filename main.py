from pipeline import run_checkpoint

if __name__ == "__main__":
    output = run_checkpoint("Python")

    print("\n📘 Final Context:\n")
    print(output["context"])

    print("\n📊 Metadata:")
    print("Source:", output["source"])
    print("Relevance Score:", output["relevance_score"])
