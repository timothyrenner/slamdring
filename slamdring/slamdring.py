import click
import asyncio
import aiohttp
import csv

from toolz import curry


def _csv_reader(file_handle, delimiter=","):
    return csv.reader(file_handle, delimiter=delimiter)


def _csv_dict_reader(file_handle, delimiter=","):
    return csv.DictReader(file_handle, delimiter=delimiter)


def _list_extractor(request_record):
    return request_record[-1]


def _dict_extractor(request_record, request_field="request"):
    return request_record[request_field]


def _append_processor(request_record, response):
    if isinstance(request_record, list):
        return request_record + [response]
    else:
        return {
            "response": response,
            **request_record
        }


def _csv_writer(file_handle, delimiter=","):
    return csv.writer(file_handle, delimiter=delimiter)


def _csv_dict_writer(file_handle, fieldnames, delimiter=","):
    return csv.DictWriter(file_handle, delimiter=",", fieldnames=fieldnames)


async def process_records(request_queue, response_queue, extractor, processor):
    """ Reads from the request queue in a loop, issues HTTP requests, and
        puts the responses on the response queue.

        Parameters:
            request_queue - The queue to read requests from.
            response_queue - The queue to put the responses on.
            extractor - A function that takes a request record and returns the
                request to perform.
            processor - A function that takes a request record and a response
                and creates a response record to pass to the writer.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            request_record = await request_queue.get()

            request = extractor(request_record)

            async with session.get(request) as response:
                read_response = await response.text()
                # Add the response to the request record.
                response_record = processor(request_record, read_response)

                await response_queue.put(response_record)
                request_queue.task_done()


async def write_records(response_queue, writer):
    """ Reads the responses from the response queue and writes it to the writer.

        Parameters:
            response_queue - The queue with the API responses.
            writer - The writer to write the responses with.
    """
    while True:

        response_record = await response_queue.get()

        writer.writerow(response_record)
        response_queue.task_done()


async def slam(
    input_file,
    output_file,
    num_tasks,
    delimiter,
    format,
    request_field
):
    """ Sets up the async queues and tasks and executes the requests.

        Parameters:
            input_file - The file to read requests from.
            output_file - The file to write responses to.
            num_tasks - The number of processor tasks to issue requests with.
            delimiter - The delimiter of the input and output files.
    """
    request_queue = asyncio.Queue()
    response_queue = asyncio.Queue()

    if format == "csv":
        reader = _csv_reader(input_file, delimiter=delimiter)
        writer = _csv_writer(output_file, delimiter=delimiter)
        extractor = _list_extractor
    elif format == "csv-header":
        reader = _csv_dict_reader(input_file, delimiter=delimiter)
        fields = reader.fieldnames
        writer = _csv_dict_writer(
            output_file,
            delimiter=delimiter,
            fieldnames=fields+["response"]
        )
        writer.writeheader()
        extractor = curry(_dict_extractor)(request_field=request_field)

    processor_tasks = [
        asyncio.ensure_future(
            process_records(
                request_queue,
                response_queue,
                extractor,
                _append_processor
            )
        )
        for ii in range(num_tasks)
    ]

    writer_task = asyncio.ensure_future(write_records(response_queue, writer))

    # Lazily put the rows in the queue.
    for row in reader:
        await request_queue.put(row)

    # Wait until queues are complete.
    await request_queue.join()
    await response_queue.join()

    # Shutdown all tasks.
    for task in processor_tasks:
        task.cancel()
    writer_task.cancel()


@click.command()
@click.option('--input-file', '-i', type=click.File('r'), default='-')
@click.option('--output-file', '-o', type=click.File('w'), default='-')
@click.option('--num-tasks', '-n', type=int, default=1)
@click.option('--delimiter', '-d', type=str, default=",")
@click.option(
    '--format', '-f',
    type=click.Choice(["csv", "csv-header"]),
    default="csv"
)
@click.option('--request-field', '-r', type=str, default="request")
def cli(input_file, output_file, num_tasks, delimiter, format, request_field):
    """ Command line interface for the API hammer. Assumes the input file
        has no header, and that the last column is the column with the HTTP
        requests.
    """
    event_loop = asyncio.get_event_loop()

    event_loop.run_until_complete(
        slam(
            input_file,
            output_file,
            num_tasks,
            delimiter,
            format,
            request_field
        )
    )

    event_loop.close()
