# AutoFAQ
AutoFAQ is a sophisticated FAQ dataset mining framework designed as an interactive CLI tool for rapid and efficient data collection. With AutoFAQ, you can compile comprehensive FAQ datasets in just minutes!

### Process Overview
AutoFAQ's streamlined process follows these steps to generate a complete dataset:
- **Expand Keywords**: Provide a few initial keywords, and AutoFAQ will automatically expand the list to generate a comprehensive query list.
- **Web Search**: AutoFAQ performs searches using your choice of designated search engines to create a list of relevant webpages.
- **Information Extraction**: Once all webpages are downloaded, AutoFAQ extracts QA pairs using the available extractor engines.
- **Data Cleaning**: AutoFAQ's cleaning modules allow you to refine the dataset using semantic entailment of QA pairs, titles, or pages.
- **Rendering**: Finally, you can render the dataset into your desired format with ease. Success!

## Getting Started
0. Install the `autofaq` CLI tool using:
    ```sh
    pip install autofaq
    ```
1.
    ```sh 
    Usage: autofaq [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    clean     Refines the dataset
    embed     Computes vector embeddings of the dataset
    extract   Collects webpages and extracts QA pairs
    init      Initiates a new mining project
    keywords  Generates an expanded list of keywords
    render    Transforms the dataset into human-readable formats
    search    Compiles search results for keywords
    ```