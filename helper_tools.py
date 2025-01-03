QA_TOOLS = [
    {
        "name": "evaluate_qa_pairs",
        "description": (
            "Evaluate two responses provided for a given question and determine which response is superior based on its directness and clarity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "The preferred response, either 'Response A' or 'Response B'."
                },
                "reasoning": {
                    "type": "string",
                    "description": (
                        "A single-sentence explanation justifying why the selected response is better. This should highlight how it is more direct and clear in addressing the question."
                    )
                }
            },
            "required": ["response", "reasoning"]
        }
    }
]


def generate_prompt(start_idx: int, end_idx: int, report_type: str, report_title: str, example_headers: str, output_example: str) -> str:

    """
    Generates a customizable prompt for analyzing pages of a report and extracting structured information.
    
    This function creates a detailed instruction prompt that guides an AI model to:
    1. Analyze specific pages of a report
    2. Extract page titles and create content-based questions
    3. Generate multiple answers for each question
    4. Format the output as a JSON array
    
    Parameters:
    ----------
    start_idx : int
        Starting page number of the analysis
    end_idx : int
        Ending page number of the analysis
    report_type : str
        The type of report being analyzed (financial, market, etc.)
    report_title : str
        The title of the report being analyzed
    example_headers : str
        Example section headers from the report to guide title extraction
    output_example : str
        JSON format example output string to demonstrate expected structure
    
    Returns:
    -------
    str
        A formatted prompt string containing instructions and examples for report analysis
    """

    return f"""
    You are an expert at analyzing {report_type} and generating question-answer pairs. For the provided PDF, {report_title}:

    1. Analyze pages {start_idx} to {end_idx} and for **each** of those pages:
        - Identify the **exact page title** as it appears on that page (e.g., "{example_headers}").
        - If the page includes a chart, graph, or diagram, create a question that references that visual element. Otherwise, create a question about the textual content.
        - Generate two distinct answers to that question ("answer_1" and "answer_2"), both supported by the page’s content.
        - Identify the correct page number as indicated in the bottom left corner of the page.
    2. Return exactly {end_idx - start_idx + 1} results as a valid JSON array (a list of dictionaries). Each dictionary should have the keys: “page” (int), “page_title” (str), “question” (str), “answer_1” (str), and “answer_2” (str).
    3. Do not include any other text or comments.

    Below is an example of the output format:

    {output_example}

    Double-check your output to ensure each of the JSON objects includes the correct page number, exact page title, a non-obvious question, and two supported answers.
    """
