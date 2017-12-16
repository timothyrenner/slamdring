import click
import asyncio
import aiohttp
import csv
import json

from toolz import curry, identity, dissoc


def _safe_json_parse(record):
    try:
        return json.loads(record)
    except json.JSONDecodeError:
        return record


def _csv_reader(file_handle, delimiter=","):
    return csv.reader(file_handle, delimiter=delimiter)


def _csv_dict_reader(file_handle, delimiter=","):
    return csv.DictReader(file_handle, delimiter=delimiter)


def _json_reader(file_handle):
    return map(json.loads, file_handle)


def _list_extractor(request_record, request_field=-1):
    return request_record[request_field]


def _dict_extractor(request_record, request_field="request"):
    return request_record[request_field]


def _list_append_processor(request_record, response):
    return request_record + [response]


def _list_replace_processor_negative(request_record, response, request_field):
    return request_record[:len(request_record)+request_field] + \
        request_record[len(request_record)+request_field+1:] + \
        [response]


def _list_replace_processor(request_record, response, request_field):
    return request_record[:request_field] + \
        request_record[request_field+1:] + \
        [response]


def _dict_append_processor(
    request_record,
    response,
    parse=identity,
    request_field="request",
    response_field="response"
):
    return {
        response_field: parse(response),
        **request_record
    }


def _dict_replace_processor(
    request_record, \
    response, 
    parse=identity,
    request_field="request",
    response_field="response"
):
    return {
        response_field: parse(response),
        **dissoc(request_record, request_field)
    }


def _csv_write(writer, record):
    writer.writerow(record)


def _json_write(writer, record):
    writer.write(json.dumps(record) + "\n")


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


async def write_records(response_queue, write):
    """ Reads the responses from the response queue and writes it to the writer.

        Parameters:
            response_queue - The queue with the API responses.
            write - A function that writes the record to a file / stdout.
    """
    while True:

        response_record = await response_queue.get()

        write(response_record)
        response_queue.task_done()


async def slam(
    input_file,
    output_file,
    num_tasks,
    delimiter,
    format,
    request_field,
    response_field,
    no_repeat_request
):
    """ Sets up the async queues and tasks and executes the requests.
    """
    request_queue = asyncio.Queue()
    response_queue = asyncio.Queue()

    if format == "csv":
        reader = _csv_reader(input_file, delimiter=delimiter)
        write = curry(_csv_write)(csv.writer(output_file, delimiter=delimiter))
        # If the request field is the default "request", translate that into
        # the last column. Otherwise convert the option into an integer.
        extractor = curry(_list_extractor)(
            request_field=(
                -1 if request_field == "request" else int(request_field)
            )
        )

        # Select the processor based on whether the request field is being
        # repeated, and whether the column provided for the request is a 
        # negative or positive integer.
        request_field_int = -1 if request_field == "request" \
            else int(request_field)
        if no_repeat_request and request_field_int < 0:
            processor = curry(_list_replace_processor_negative)(
                request_field=request_field_int
            )
        elif no_repeat_request:
            processor = curry(_list_replace_processor)(
                request_field=request_field_int
            )
        else:
            processor = _list_append_processor

    elif format == "csv-header":
        reader = _csv_dict_reader(input_file, delimiter=delimiter)
        # Use the field names from the reader for the writer.
        fields = reader.fieldnames
        writer = csv.DictWriter(
            output_file,
            delimiter=delimiter,
            fieldnames=fields+[response_field]
        )
        # Write the header before doing anything else.
        writer.writeheader()
        # Construct the rest of the helpers.
        write = curry(_csv_write)(writer)
        extractor = curry(_dict_extractor)(request_field=request_field)
        processor = curry(
            _dict_replace_processor if no_repeat_request
            else _dict_append_processor
        )(request_field=request_field, response_field=response_field)

    elif format == "json":
        reader = _json_reader(input_file)
        write = curry(_json_write)(output_file)
        extractor = curry(_dict_extractor)(request_field=request_field)
        processor = curry(
            _dict_replace_processor if no_repeat_request 
            else _dict_append_processor
        )(
            request_field=request_field,
            response_field=response_field,
            parse=_safe_json_parse
        )

    processor_tasks = [
        asyncio.ensure_future(
            process_records(
                request_queue,
                response_queue,
                extractor,
                processor
            )
        )
        for ii in range(num_tasks)
    ]

    writer_task = asyncio.ensure_future(write_records(response_queue, write))

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
@click.option(
    '--input-file', '-i',
    type=click.File('r'),
    default='-',
    help="The input file to read from. Default: STDIN."
)
@click.option(
    '--output-file', '-o',
    type=click.File('w'),
    default='-',
    help="The output file to write to. Default: STDOUT."
)
@click.option(
    '--num-tasks', '-n',
    type=int,
    default=1,
    help="The number of async tasks to issue requests from. Default: 1."
)
@click.option(
    '--delimiter', '-d',
    type=str,
    default=",",
    help="The delimiter for CSV formats. Default: , ."
)
@click.option(
    '--format', '-f',
    type=click.Choice(["csv", "csv-header", "json"]),
    default="csv",
    help="The file format for inputs / outputs. Default: csv."
)
@click.option(
    '--request-field', '-r',
    type=str,
    default="request",
    help="The name of the field with the request. Default: request "
    "(csv-header,json) or last column (csv)."
)
@click.option(
    '--response-field', '-R',
    type=str,
    default="response",
    help="The name of the field to put the response into for csv-header and "
    "json formats."
)
@click.option(
    '--no-repeat-request',
    is_flag=True,
    default=False,
    help="Don't reprint the request field in the output."
)
def cli(
    input_file, 
    output_file, 
    num_tasks, 
    delimiter, 
    format, 
    request_field,
    response_field,
    no_repeat_request
):
    """ The API hammer. Issues concurrent HTTP GET requests in an async event
        loop.
    """
    event_loop = asyncio.get_event_loop()

    event_loop.run_until_complete(
        slam(
            input_file,
            output_file,
            num_tasks,
            delimiter,
            format,
            request_field,
            response_field,
            no_repeat_request
        )
    )

    event_loop.close()
