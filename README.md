# Slamdring, the API Hammer

> Turgon, King of Gondolin, wields, has, and holds the tool Slamdring, Foe of HTTP's realm, Hammer of the APIs.

Slamdring is a command line tool for issuing large numbers of HTTP GET requests concurrently.
It's primary use case is data collection - when data is behind a REST API without bulk access it can take a while to sit and wait for a non-async HTTP library like `requests` to do its thing.
This tool will read URLs in delimited data from STDIN or a file, issue the GETs at a configurable level of concurrency, and write the exact same data with the response added as a new field to either STDOUT or a file.

**THIS IS A HOBBY PROJECT.**
I started this for a specific use-case but then saw a pattern and generalized it.
Mostly I wrote it to learn Python's async facilities.
In any case, this is definitely hobby code, not production code.

Currently this tool needs to be cloned and installed locally.

```shell
# git clone ...
# cd into project directory.

pip install -e .
```

Here's how to use it.
First, you need a file with all of the requests in it.
There's an example file in `data/test_data_csv_comma.csv`.
It looks like this:

```
1,https://jsonplaceholder.typicode.com/posts/1
2,https://jsonplaceholder.typicode.com/posts/2
3,https://jsonplaceholder.typicode.com/posts/3
4,https://jsonplaceholder.typicode.com/posts/4
5,https://jsonplaceholder.typicode.com/posts/5
6,https://jsonplaceholder.typicode.com/posts/6
7,https://jsonplaceholder.typicode.com/posts/7
8,https://jsonplaceholder.typicode.com/posts/8
9,https://jsonplaceholder.typicode.com/posts/9
10,https://jsonplaceholder.typicode.com/posts/10
```

Standard CSV, no header, with the requests in the last column.
The other columns could be anything, but it's probably most useful for those to either be _all_ of the other columns you want in your final dataset, or at the very least a join key back to the rest of the data.
There's more than one way to invoke slamdring to fill out responses for this massive number of requests.

```shell
# Using args for the files.
slamdring --input-file data/test_data_csv_comma.csv --output-file resp.csv --num-tasks 5

# Defaults for input and output files are STDIN and STDOUT.
cat data/test_data_csv_comma.csv | slamdring --num-tasks 3 > resp.csv
```

The `resp.csv` file will look something like this:

```
3,https://jsonplaceholder.typicode.com/posts/3,"{
  ""userId"": 1,
  ""id"": 3,
  ""title"": ""ea molestias quasi exercitationem repellat qui ipsa sit aut"",
  ""body"": ""et iusto sed quo iure\nvoluptatem occaecati omnis eligendi aut ad\nvoluptatem doloribus vel accusantium quis pariatur\nmolestiae porro eius odio et labore et velit aut""
}"
2,https://jsonplaceholder.typicode.com/posts/2,"{
  ""userId"": 1,
  ""id"": 2,
  ""title"": ""qui est esse"",
  ""body"": ""est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla""
}"

# ... and so forth.
```

It looks exactly like the input file with a new column containing the response.
Note that it's not in the same order.

Slamdring also works with CSVs that have a header (`--format csv-header`) and line delimited JSON files (`--format json`).
For those formats, the response is put in a "response" field.
For json, the response is parsed at the same "level" as the rest of the fields so each record in the output doesn't need to parse the response separately (unlike the CSV formats).

See below for the full list of options available:

```
Usage: slamdring [OPTIONS]

  The API hammer. Issues concurrent HTTP GET requests in an async event
  loop.

Options:
  -i, --input-file FILENAME       The input file to read from. Default: STDIN.
  -o, --output-file FILENAME      The output file to write to. Default:
                                  STDOUT.
  -n, --num-tasks INTEGER         The number of async tasks to issue requests
                                  from. Default: 1.
  -d, --delimiter TEXT            The delimiter for CSV formats. Default: , .
  -f, --format [csv|csv-header|json]
                                  The file format for inputs / outputs.
                                  Default: csv.
  -r, --request-field TEXT        The name of the field with the request.
                                  Default: request (csv-header,json) or last
                                  column (csv).
  -R, --response-field TEXT       The name of the field to put the response
                                  into for csv-header and json formats.
  --repeat-request / --no-repeat-request
                                  Whether to reprint the request field in the
                                  output.
  --help                          Show this message and exit.
```

Note that the output file format always matches the input file format.
This might change in the future, or it might not.

## Performance

Slamdring is significantly faster than a set of serial blocking calls using vanilla  `requests` (there are some libraries that do provide async capability for requests, but the regular requests is synchronous and blocking).
For 10,000 queries against a simple local server in Node, requests takes about 30 seconds.
Slamdring performs the same set of queries in 5-6 seconds.

To check this yourself, run and start [`json-server`](https://github.com/typicode/json-server) and use an empty `db.json` like so:

```shell
npm install -g json-server

json-server db.json
# json-server makes phony data here since db.json is empty.
```

That server's running on `localhost:3000/`.
Next run 

```
python scripts/make_requests.py
```

This makes 10,000 phony requests in a csv - all the same - and puts them in `data/test_data_large.csv`.

Run the requests version first.

```
time python scripts/get_requests.py

# On my machine, 
# real    0m29.553s
# user    0m19.837s
# sys     0m1.590s
```

Now, using slamdring,

```
time slamdring -i data/test_data_large_responses.csv -o data/test_data_large_responses_2.csv -n 10

# On my machine,
# real    0m5.910s
# user    0m5.295s
# sys     0m0.211s
```

The gains are even greater when there's real latency involved.
If each request had a half second latency then with slamdring I can just up the number of concurrent tasks and slam that server.
With a blocking version I just have to wait.

## How it Works

Probably the best way to understand slamdring is to just look at the code.
It's extremely simple (well, as simple as Python's async facilities allow) and should be easy to read.

Slamdring uses Python's [asyncio](http://asyncio.readthedocs.io/en/latest/index.html) module with [aiohttp](https://aiohttp.readthedocs.io/en/stable/) to issue lots of HTTP requests concurrently.
It reads from the csv file and drops each row onto a [queue](http://asyncio.readthedocs.io/en/latest/producer_consumer.html), which the worker tasks pick up (these are specified by `-n` or `--num-tasks`) and issue the requests.
Within each of _those_ tasks, they block until the server responds, but we can have a whole lot of these tasks waiting at once.
_This isn't the only way to implement this kind of work_, but I think queues are very simple compared to stuff like Semaphores and whatnot.

Whenever a task completes it goes onto another queue, this one with only one worker reading from it.
All that worker does is write the response to a file, so compared to our poor HTTP server and our worker tasks, it's doing a lot less work.
The reason I only put one writer task is for consistency - with multiple tasks writing to a single file there might be some inconsistency in the records (i.e. one record clobbers another on the same line).
It's possible to have each consumer write to it's own file and merge them at the end, but that's not a high latency output task, so I'm not sure there's a lot to gain.
By contrast dropping into a database or issuing a bunch of PUTs _is_ a high latency output task, so maybe there's a future use case there.
For now I'm sticking with CSV files because I'm a data scientist and that's all I know :).

## Tests

There's a suite of regression tests in there if you want to run those for some reason.
First, start up `json-server` (`npm install -g json-server`, then `json-server db.json`), then run

```
scripts/checkup.sh
```