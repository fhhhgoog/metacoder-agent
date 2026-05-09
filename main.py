import logging
from pathlib import Path


LOG_FILE = Path(__file__).with_name("metacoder_agent.log")
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

workflow_logger = logging.getLogger("Workflow")
reviewer_logger = logging.getLogger("Reviewer")
coder_logger = logging.getLogger("Coder")


def configure_logging():
    """Configure console and file logging for the MetaCoder-Agent workflow."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def call_agent(role_prompt, user_content, temperature=0.2):
    """Mock Agent call for local workflow validation without network requests."""
    if role_prompt == "reviewer":
        if "if not metrics_list" in user_content:
            return "PASS"
        if "avg = total / len(metrics_list)" in user_content:
            return "发现潜在缺陷：当 metrics_list 为空列表时，len(metrics_list) 为 0，会触发 ZeroDivisionError。建议在计算平均值前先处理空列表。"
        return "PASS"

    if role_prompt == "coder":
        return """def calculate_average(metrics_list):
    if not metrics_list:
        return 0
    total = sum(metrics_list)
    avg = total / len(metrics_list)
    return avg
"""

    return "Mock response: no action needed."


def reviewer_agent(code_snippet):
    """Reviewer Agent: finds defects in the code snippet."""
    reviewer_logger.info("Analyzing current code snippet.")
    return call_agent("reviewer", code_snippet)


def coder_agent(code_snippet, review_feedback):
    """Coder Agent: repairs code according to review feedback."""
    coder_logger.info("Preparing repair based on reviewer feedback.")
    content = f"Original code:\n{code_snippet}\n\nReview feedback:\n{review_feedback}"
    return call_agent("coder", content)


def agentic_workflow_loop(initial_code, max_iterations=3):
    """Core loop: Reviewer finds issues, Coder repairs, then Reviewer checks again."""
    workflow_logger.info("Workflow started: initiating code review and repair loop.")
    current_code = initial_code

    for i in range(max_iterations):
        workflow_logger.info("Iteration %s started.", i + 1)

        feedback = reviewer_agent(current_code)

        if "PASS" in feedback.upper() and len(feedback) < 15:
            reviewer_logger.info("Approved the code. Workflow complete.")
            break

        reviewer_logger.warning("Found issues:\n%s", feedback)

        coder_logger.info("Rewriting code based on feedback.")
        current_code = coder_agent(current_code, feedback)
        coder_logger.info("New code generated:\n%s", current_code)

    return current_code


if __name__ == "__main__":
    configure_logging()

    bad_code = """
def calculate_average(metrics_list):
    total = sum(metrics_list)
    avg = total / len(metrics_list)
    return avg
    """

    final_code = agentic_workflow_loop(bad_code)
    workflow_logger.info("Final output:\n%s", final_code)
