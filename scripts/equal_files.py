import click
import json
import csv

from toolz import dissoc

@click.command()
@click.argument('answer_file', type=click.File('r'))
@click.argument('truth_file', type=click.File('r'))
@click.option(
    '--format', '-f', 
    type=click.Choice(['csv', 'csv-header', 'json']), 
    default='csv'
)
@click.option('--delimiter', '-d', type=str, default=',')
def main(answer_file, truth_file, format, delimiter):
    if format == "csv":
        answer_reader = csv.reader(answer_file, delimiter=delimiter)
        truth_reader = csv.reader(truth_file, delimiter=delimiter)
    elif format == "csv-header":
        answer_reader = csv.DictReader(answer_file, delimiter=delimiter)
        truth_reader = csv.DictReader(truth_file, delimiter=delimiter)
    elif format == "json":
        answer_reader = map(json.loads, answer_file)
        truth_reader = map(json.loads, truth_file)

    answer_lines = [line for line in answer_reader]
    truth_lines = [line for line in truth_reader]

    if len(answer_lines) != len(truth_lines):
        print("{} has {} lines, but {} has {} lines.".format(
            answer_file.name,
            len(answer_lines),
            truth_file.name,
            len(truth_lines)
        ))

    for answer,truth in zip(answer_lines, truth_lines):
        if format == "csv":
            answer_request = answer[:-1]
            answer_response = json.loads(answer[-1])
            truth_request = truth[:-1]
            truth_response = json.loads(truth[-1])
        elif format == "csv-header":
            answer_request = dissoc(answer, "response")
            answer_response = json.loads(answer["response"])
            truth_request = dissoc(truth, "response")
            truth_response = json.loads(truth["response"])
        elif format == "json":
            answer_request = dissoc(answer, "response")
            answer_response = answer["response"]
            truth_request = dissoc(truth, "response")
            truth_response = truth["response"]
        
        if answer_request != truth_request:
            print("{} is not equal to {}.".format(
                answer_request,
                truth_request
            ))

        if answer_response != truth_response:
            print("{} is not equal to {}.".format(
                answer_response,
                truth_response
            ))

    print("Done checking {} against {}.".format(
        answer_file.name,
        truth_file.name
    ))

if __name__ == "__main__":
    main()
