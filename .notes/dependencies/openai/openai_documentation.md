(Files content cropped to 300k characters, download full ingest to see more)
================================================
File: /README.md
================================================
# OpenAI Python API library

[![PyPI version](https://img.shields.io/pypi/v/openai.svg)](https://pypi.org/project/openai/)

The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.8+
application. The library includes type definitions for all request params and response fields,
and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

It is generated from our [OpenAPI specification](https://github.com/openai/openai-openapi) with [Stainless](https://stainlessapi.com/).

## Documentation

The REST API documentation can be found on [platform.openai.com](https://platform.openai.com/docs). The full API of this library can be found in [api.md](api.md).

## Installation

> [!IMPORTANT]
> The SDK was rewritten in v1, which was released November 6th 2023. See the [v1 migration guide](https://github.com/openai/openai-python/discussions/742), which includes scripts to automatically update your code.

```sh
# install from PyPI
pip install openai
```

## Usage

The full API of this library can be found in [api.md](api.md).

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)
```

While you can provide an `api_key` keyword argument,
we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)
to add `OPENAI_API_KEY="My API Key"` to your `.env` file
so that your API Key is not stored in source control.

### Vision

With a hosted image:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"{img_url}"},
                },
            ],
        }
    ],
)
```

With the image as a base64 encoded string:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{img_type};base64,{img_b64_str}"},
                },
            ],
        }
    ],
)
```

### Polling Helpers

When interacting with the API some actions such as starting a Run and adding files to vector stores are asynchronous and take time to complete. The SDK includes
helper functions which will poll the status until it reaches a terminal state and then return the resulting object.
If an API method results in an action that could benefit from polling there will be a corresponding version of the
method ending in '\_and_poll'.

For instance to create a Run and poll until it reaches a terminal state you can run:

```python
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)
```

More information on the lifecycle of a Run can be found in the [Run Lifecycle Documentation](https://platform.openai.com/docs/assistants/how-it-works/run-lifecycle)

### Bulk Upload Helpers

When creating and interacting with vector stores, you can use polling helpers to monitor the status of operations.
For convenience, we also provide a bulk upload helper to allow you to simultaneously upload several files at once.

```python
sample_files = [Path("sample-paper.pdf"), ...]

batch = await client.vector_stores.file_batches.upload_and_poll(
    store.id,
    files=sample_files,
)
```

### Streaming Helpers

The SDK also includes helpers to process streams and handle incoming events.

```python
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
) as stream:
    for event in stream:
        # Print the text from text delta events
        if event.type == "thread.message.delta" and event.data.delta.content:
            print(event.data.delta.content[0].text)
```

More information on streaming helpers can be found in the dedicated documentation: [helpers.md](helpers.md)

## Async usage

Simply import `AsyncOpenAI` instead of `OpenAI` and use `await` with each API call:

```python
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-4o",
    )


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

## Streaming responses

We provide support for streaming responses using Server Side Events (SSE).

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

The async client uses the exact same interface.

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main():
    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test"}],
        stream=True,
    )
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")


asyncio.run(main())
```

## Module-level client

> [!IMPORTANT]
> We highly recommend instantiating client instances instead of relying on the global client.

We also expose a global client instance that is accessible in a similar fashion to versions prior to v1.

```py
import openai

# optional; defaults to `os.environ['OPENAI_API_KEY']`
openai.api_key = '...'

# all client options can be configured just like the `OpenAI` instantiation counterpart
openai.base_url = "https://..."
openai.default_headers = {"x-foo": "true"}

completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.choices[0].message.content)
```

The API is the exact same as the standard client instance-based API.

This is intended to be used within REPLs or notebooks for faster iteration, **not** in application code.

We recommend that you always instantiate a client (e.g., with `client = OpenAI()`) in application code because:

- It can be difficult to reason about where client options are configured
- It's not possible to change certain client options without potentially causing race conditions
- It's harder to mock for testing purposes
- It's not possible to control cleanup of network connections

## Realtime API beta

The Realtime API enables you to build low-latency, multi-modal conversational experiences. It currently supports text and audio as both input and output, as well as [function calling](https://platform.openai.com/docs/guides/function-calling) through a WebSocket connection.

Under the hood the SDK uses the [`websockets`](https://websockets.readthedocs.io/en/stable/) library to manage connections.

The Realtime API works through a combination of client-sent events and server-sent events. Clients can send events to do things like update session configuration or send text and audio inputs. Server events confirm when audio responses have completed, or when a text response from the model has been received. A full event reference can be found [here](platform.openai.com/docs/api-reference/realtime-client-events) and a guide can be found [here](https://platform.openai.com/docs/guides/realtime).

Basic text based example:

```py
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as connection:
        await connection.session.update(session={'modalities': ['text']})

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == 'response.text.delta':
                print(event.delta, flush=True, end="")

            elif event.type == 'response.text.done':
                print()

            elif event.type == "response.done":
                break

asyncio.run(main())
```

However the real magic of the Realtime API is handling audio inputs / outputs, see this example [TUI script](https://github.com/openai/openai-python/blob/main/examples/realtime/push_to_talk_app.py) for a fully fledged example.

### Realtime error handling

Whenever an error occurs, the Realtime API will send an [`error` event](https://platform.openai.com/docs/guides/realtime/realtime-api-beta#handling-errors) and the connection will stay open and remain usable. This means you need to handle it yourself, as *no errors are raised directly* by the SDK when an `error` event comes in.

```py
client = AsyncOpenAI()

async with client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as connection:
    ...
    async for event in connection:
        if event.type == 'error':
            print(event.error.type)
            print(event.error.code)
            print(event.error.event_id)
            print(event.error.message)
```

## Using types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON, `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

## Pagination

List methods in the OpenAI API are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

```python
from openai import OpenAI

client = OpenAI()

all_jobs = []
# Automatically fetches more pages as needed.
for job in client.fine_tuning.jobs.list(
    limit=20,
):
    # Do something with job here
    all_jobs.append(job)
print(all_jobs)
```

Or, asynchronously:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main() -> None:
    all_jobs = []
    # Iterate through items across all pages, issuing requests as needed.
    async for job in client.fine_tuning.jobs.list(
        limit=20,
    ):
        all_jobs.append(job)
    print(all_jobs)


asyncio.run(main())
```

Alternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")

# Remove `await` for non-async usage.
```

Or just work directly with the returned data:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)

print(f"next page cursor: {first_page.after}")  # => "next page cursor: ..."
for job in first_page.data:
    print(job.id)

# Remove `await` for non-async usage.
```

## Nested params

Nested parameters are dictionaries, typed using `TypedDict`, for example:

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Can you generate an example json object describing a fruit?",
        }
    ],
    model="gpt-4o",
    response_format={"type": "json_object"},
)
```

## File uploads

Request parameters that correspond to file uploads can be passed as `bytes`, a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

The async client uses the exact same interface. If you pass a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, the file contents will be read asynchronously automatically.

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `openai.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `openai.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `openai.APIError`.

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    client.fine_tuning.jobs.create(
        model="gpt-4o",
        training_file="file-abc123",
    )
except openai.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except openai.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except openai.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as followed:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

## Request IDs

> For more information on debugging requests, see [these docs](https://platform.openai.com/docs/api-reference/debugging-requests)

All object responses in the SDK provide a `_request_id` property which is added from the `x-request-id` response header so that you can quickly log failing requests and report them back to OpenAI.

```python
completion = await client.chat.completions.create(
    messages=[{"role": "user", "content": "Say this is a test"}], model="gpt-4"
)
print(completion._request_id)  # req_123
```

Note that unlike other properties that use an `_` prefix, the `_request_id` property
*is* public. Unless documented otherwise, *all* other `_` prefix properties,
methods and modules are *private*.


### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I get the name of the current day in JavaScript?",
        }
    ],
    model="gpt-4o",
)
```

### Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration) object:

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # 20 seconds (default is 10 minutes)
    timeout=20.0,
)

# More granular control:
client = OpenAI(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I list all files in a directory using Python?",
        }
    ],
    model="gpt-4o",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `OPENAI_LOG` to `info`.

```shell
$ export OPENAI_LOG=info
```

Or to `debug` for more verbose logging.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.with_raw_response.create(
    messages=[{
        "role": "user",
        "content": "Say this is a test",
    }],
    model="gpt-4o",
)
print(response.headers.get('X-My-Header'))

completion = response.parse()  # get the object that `chat.completions.create()` would have returned
print(completion)
```

These methods return an [`LegacyAPIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_legacy_response.py) object. This is a legacy class as we're changing it slightly in the next major version.

For the sync client this will mostly be the same with the exception
of `content` & `text` will be methods instead of properties. In the
async client, all methods will be async.

A migration script will be provided & the migration in general should
be smooth.

#### `.with_streaming_response`

The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use `.with_streaming_response` instead, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`. In the async client, these are async methods.

As such, `.with_streaming_response` methods return a different [`APIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_response.py) object, and the async client returns an [`AsyncAPIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_response.py) object.

```python
with client.chat.completions.with_streaming_response.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

The context manager is required so that the response will reliably be closed.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can make requests using `client.get`, `client.post`, and other
http verbs. Options on the client will be respected (such as retries) will be respected when making this
request.

```py
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

#### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request
options.

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You
can also get all the extra fields on the Pydantic model as a dict with
[`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for [proxies](https://www.python-httpx.org/advanced/proxies/)
- Custom [transports](https://www.python-httpx.org/advanced/transports/)
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
import httpx
from openai import OpenAI, DefaultHttpxClient

client = OpenAI(
    # Or use the `OPENAI_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

You can also customize the client on a per-request basis by using `with_options()`:

```python
client.with_options(http_client=DefaultHttpxClient(...))
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

```py
from openai import OpenAI

with OpenAI() as client:
  # make requests here
  ...

# HTTP client is now closed
```

## Microsoft Azure OpenAI

To use this library with [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/overview), use the `AzureOpenAI`
class instead of the `OpenAI` class.

> [!IMPORTANT]
> The Azure API shape differs from the core API shape which means that the static types for responses / params
> won't always be correct.

```py
from openai import AzureOpenAI

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
    api_version="2023-07-01-preview",
    # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
```

In addition to the options provided in the base `OpenAI` client, the following options are provided:

- `azure_endpoint` (or the `AZURE_OPENAI_ENDPOINT` environment variable)
- `azure_deployment`
- `api_version` (or the `OPENAI_API_VERSION` environment variable)
- `azure_ad_token` (or the `AZURE_OPENAI_AD_TOKEN` environment variable)
- `azure_ad_token_provider`

An example of using the client with Microsoft Entra ID (formerly known as Azure Active Directory) can be found [here](https://github.com/openai/openai-python/blob/main/examples/azure_ad.py).

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals)_.
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/openai/openai-python/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```py
import openai
print(openai.__version__)
```

## Requirements

Python 3.8 or higher.

## Contributing

See [the contributing documentation](./CONTRIBUTING.md).


================================================
File: /Brewfile
================================================
brew "rye"



================================================
File: /CONTRIBUTING.md
================================================
## Setting up the environment

### With Rye

We use [Rye](https://rye.astral.sh/) to manage dependencies because it will automatically provision a Python environment with the expected Python version. To set it up, run:

```sh
$ ./scripts/bootstrap
```

Or [install Rye manually](https://rye.astral.sh/guide/installation/) and run:

```sh
$ rye sync --all-features
```

You can then run scripts using `rye run python script.py` or by activating the virtual environment:

```sh
$ rye shell
# or manually activate - https://docs.python.org/3/library/venv.html#how-venvs-work
$ source .venv/bin/activate

# now you can omit the `rye run` prefix
$ python script.py
```

### Without Rye

Alternatively if you don't want to install `Rye`, you can stick with the standard `pip` setup by ensuring you have the Python version specified in `.python-version`, create a virtual environment however you desire and then install dependencies using this command:

```sh
$ pip install -r requirements-dev.lock
```

## Modifying/Adding code

Most of the SDK is generated code. Modifications to code will be persisted between generations, but may
result in merge conflicts between manual patches and changes from the generator. The generator will never
modify the contents of the `src/openai/lib/` and `examples/` directories.

## Adding and running examples

All files in the `examples/` directory are not modified by the generator and can be freely edited or added to.

```py
# add an example to examples/<your-example>.py

#!/usr/bin/env -S rye run python
…
```

```sh
$ chmod +x examples/<your-example>.py
# run the example against your api
$ ./examples/<your-example>.py
```

## Using the repository from source

If you’d like to use the repository from source, you can either install from git or link to a cloned repository:

To install via git:

```sh
$ pip install git+ssh://git@github.com/openai/openai-python.git
```

Alternatively, you can build from source and install the wheel file:

Building this package will create two files in the `dist/` directory, a `.tar.gz` containing the source files and a `.whl` that can be used to install the package efficiently.

To create a distributable version of the library, all you have to do is run this command:

```sh
$ rye build
# or
$ python -m build
```

Then to install:

```sh
$ pip install ./path-to-wheel-file.whl
```

## Running tests

Most tests require you to [set up a mock server](https://github.com/stoplightio/prism) against the OpenAPI spec to run the tests.

```sh
# you will need npm installed
$ npx prism mock path/to/your/openapi.yml
```

```sh
$ ./scripts/test
```

## Linting and formatting

This repository uses [ruff](https://github.com/astral-sh/ruff) and
[black](https://github.com/psf/black) to format the code in the repository.

To lint:

```sh
$ ./scripts/lint
```

To format and fix all ruff issues automatically:

```sh
$ ./scripts/format
```

## Publishing and releases

Changes made to this repository via the automated release PR pipeline should publish to PyPI automatically. If
the changes aren't made through the automated pipeline, you may want to make releases manually.

### Publish with a GitHub workflow

You can release to package managers by using [the `Publish PyPI` GitHub action](https://www.github.com/openai/openai-python/actions/workflows/publish-pypi.yml). This requires a setup organization or repository secret to be set up.

### Publish manually

If you need to manually release a package, you can run the `bin/publish-pypi` script with a `PYPI_TOKEN` set on
the environment.


================================================
File: /LICENSE
================================================
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2025 OpenAI

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


================================================
File: /SECURITY.md
================================================
# Security Policy

## Reporting Security Issues

This SDK is generated by [Stainless Software Inc](http://stainlessapi.com). Stainless takes security seriously, and encourages you to report any security vulnerability promptly so that appropriate action can be taken.

To report a security issue, please contact the Stainless team at security@stainlessapi.com.

## Responsible Disclosure

We appreciate the efforts of security researchers and individuals who help us maintain the security of
SDKs we generate. If you believe you have found a security vulnerability, please adhere to responsible
disclosure practices by allowing us a reasonable amount of time to investigate and address the issue
before making any information public.

## Reporting Non-SDK Related Security Issues

If you encounter security issues that are not directly related to SDKs but pertain to the services
or products provided by OpenAI please follow the respective company's security reporting guidelines.

### OpenAI Terms and Policies

Our Security Policy can be found at [Security Policy URL](https://openai.com/policies/coordinated-vulnerability-disclosure-policy).

Please contact disclosure@openai.com for any questions or concerns regarding security of our services.

---

Thank you for helping us keep the SDKs and systems they interact with secure.


================================================
File: /api.md
================================================
# Shared Types

```python
from openai.types import (
    ErrorObject,
    FunctionDefinition,
    FunctionParameters,
    ResponseFormatJSONObject,
    ResponseFormatJSONSchema,
    ResponseFormatText,
)
```

# Completions

Types:

```python
from openai.types import Completion, CompletionChoice, CompletionUsage
```

Methods:

- <code title="post /completions">client.completions.<a href="./src/openai/resources/completions.py">create</a>(\*\*<a href="src/openai/types/completion_create_params.py">params</a>) -> <a href="./src/openai/types/completion.py">Completion</a></code>

# Chat

Types:

```python
from openai.types import ChatModel
```

## Completions

Types:

```python
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionAudio,
    ChatCompletionAudioParam,
    ChatCompletionChunk,
    ChatCompletionContentPart,
    ChatCompletionContentPartImage,
    ChatCompletionContentPartInputAudio,
    ChatCompletionContentPartRefusal,
    ChatCompletionContentPartText,
    ChatCompletionDeveloperMessageParam,
    ChatCompletionFunctionCallOption,
    ChatCompletionFunctionMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionModality,
    ChatCompletionNamedToolChoice,
    ChatCompletionPredictionContent,
    ChatCompletionReasoningEffort,
    ChatCompletionRole,
    ChatCompletionStreamOptions,
    ChatCompletionSystemMessageParam,
    ChatCompletionTokenLogprob,
    ChatCompletionTool,
    ChatCompletionToolChoiceOption,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/openai/resources/chat/completions.py">create</a>(\*\*<a href="src/openai/types/chat/completion_create_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion.py">ChatCompletion</a></code>

# Embeddings

Types:

```python
from openai.types import CreateEmbeddingResponse, Embedding, EmbeddingModel
```

Methods:

- <code title="post /embeddings">client.embeddings.<a href="./src/openai/resources/embeddings.py">create</a>(\*\*<a href="src/openai/types/embedding_create_params.py">params</a>) -> <a href="./src/openai/types/create_embedding_response.py">CreateEmbeddingResponse</a></code>

# Files

Types:

```python
from openai.types import FileContent, FileDeleted, FileObject, FilePurpose
```

Methods:

- <code title="post /files">client.files.<a href="./src/openai/resources/files.py">create</a>(\*\*<a href="src/openai/types/file_create_params.py">params</a>) -> <a href="./src/openai/types/file_object.py">FileObject</a></code>
- <code title="get /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">retrieve</a>(file_id) -> <a href="./src/openai/types/file_object.py">FileObject</a></code>
- <code title="get /files">client.files.<a href="./src/openai/resources/files.py">list</a>(\*\*<a href="src/openai/types/file_list_params.py">params</a>) -> <a href="./src/openai/types/file_object.py">SyncCursorPage[FileObject]</a></code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">delete</a>(file_id) -> <a href="./src/openai/types/file_deleted.py">FileDeleted</a></code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/openai/resources/files.py">content</a>(file_id) -> HttpxBinaryResponseContent</code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/openai/resources/files.py">retrieve_content</a>(file_id) -> str</code>
- <code>client.files.<a href="./src/openai/resources/files.py">wait_for_processing</a>(\*args) -> FileObject</code>

# Images

Types:

```python
from openai.types import Image, ImageModel, ImagesResponse
```

Methods:

- <code title="post /images/variations">client.images.<a href="./src/openai/resources/images.py">create_variation</a>(\*\*<a href="src/openai/types/image_create_variation_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>
- <code title="post /images/edits">client.images.<a href="./src/openai/resources/images.py">edit</a>(\*\*<a href="src/openai/types/image_edit_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>
- <code title="post /images/generations">client.images.<a href="./src/openai/resources/images.py">generate</a>(\*\*<a href="src/openai/types/image_generate_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>

# Audio

Types:

```python
from openai.types import AudioModel, AudioResponseFormat
```

## Transcriptions

Types:

```python
from openai.types.audio import (
    Transcription,
    TranscriptionSegment,
    TranscriptionVerbose,
    TranscriptionWord,
    TranscriptionCreateResponse,
)
```

Methods:

- <code title="post /audio/transcriptions">client.audio.transcriptions.<a href="./src/openai/resources/audio/transcriptions.py">create</a>(\*\*<a href="src/openai/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/openai/types/audio/transcription_create_response.py">TranscriptionCreateResponse</a></code>

## Translations

Types:

```python
from openai.types.audio import Translation, TranslationVerbose, TranslationCreateResponse
```

Methods:

- <code title="post /audio/translations">client.audio.translations.<a href="./src/openai/resources/audio/translations.py">create</a>(\*\*<a href="src/openai/types/audio/translation_create_params.py">params</a>) -> <a href="./src/openai/types/audio/translation_create_response.py">TranslationCreateResponse</a></code>

## Speech

Types:

```python
from openai.types.audio import SpeechModel
```

Methods:

- <code title="post /audio/speech">client.audio.speech.<a href="./src/openai/resources/audio/speech.py">create</a>(\*\*<a href="src/openai/types/audio/speech_create_params.py">params</a>) -> HttpxBinaryResponseContent</code>

# Moderations

Types:

```python
from openai.types import (
    Moderation,
    ModerationImageURLInput,
    ModerationModel,
    ModerationMultiModalInput,
    ModerationTextInput,
    ModerationCreateResponse,
)
```

Methods:

- <code title="post /moderations">client.moderations.<a href="./src/openai/resources/moderations.py">create</a>(\*\*<a href="src/openai/types/moderation_create_params.py">params</a>) -> <a href="./src/openai/types/moderation_create_response.py">ModerationCreateResponse</a></code>

# Models

Types:

```python
from openai.types import Model, ModelDeleted
```

Methods:

- <code title="get /models/{model}">client.models.<a href="./src/openai/resources/models.py">retrieve</a>(model) -> <a href="./src/openai/types/model.py">Model</a></code>
- <code title="get /models">client.models.<a href="./src/openai/resources/models.py">list</a>() -> <a href="./src/openai/types/model.py">SyncPage[Model]</a></code>
- <code title="delete /models/{model}">client.models.<a href="./src/openai/resources/models.py">delete</a>(model) -> <a href="./src/openai/types/model_deleted.py">ModelDeleted</a></code>

# FineTuning

## Jobs

Types:

```python
from openai.types.fine_tuning import (
    FineTuningJob,
    FineTuningJobEvent,
    FineTuningJobIntegration,
    FineTuningJobWandbIntegration,
    FineTuningJobWandbIntegrationObject,
)
```

Methods:

- <code title="post /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">create</a>(\*\*<a href="src/openai/types/fine_tuning/job_create_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">retrieve</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">list</a>(\*\*<a href="src/openai/types/fine_tuning/job_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">SyncCursorPage[FineTuningJob]</a></code>
- <code title="post /fine_tuning/jobs/{fine_tuning_job_id}/cancel">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">cancel</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/events">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">list_events</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/job_list_events_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job_event.py">SyncCursorPage[FineTuningJobEvent]</a></code>

### Checkpoints

Types:

```python
from openai.types.fine_tuning.jobs import FineTuningJobCheckpoint
```

Methods:

- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints">client.fine_tuning.jobs.checkpoints.<a href="./src/openai/resources/fine_tuning/jobs/checkpoints.py">list</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/jobs/checkpoint_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/jobs/fine_tuning_job_checkpoint.py">SyncCursorPage[FineTuningJobCheckpoint]</a></code>

# Beta

## Realtime

Types:

```python
from openai.types.beta.realtime import (
    ConversationCreatedEvent,
    ConversationItem,
    ConversationItemContent,
    ConversationItemCreateEvent,
    ConversationItemCreatedEvent,
    ConversationItemDeleteEvent,
    ConversationItemDeletedEvent,
    ConversationItemInputAudioTranscriptionCompletedEvent,
    ConversationItemInputAudioTranscriptionFailedEvent,
    ConversationItemTruncateEvent,
    ConversationItemTruncatedEvent,
    ErrorEvent,
    InputAudioBufferAppendEvent,
    InputAudioBufferClearEvent,
    InputAudioBufferClearedEvent,
    InputAudioBufferCommitEvent,
    InputAudioBufferCommittedEvent,
    InputAudioBufferSpeechStartedEvent,
    InputAudioBufferSpeechStoppedEvent,
    RateLimitsUpdatedEvent,
    RealtimeClientEvent,
    RealtimeResponse,
    RealtimeResponseStatus,
    RealtimeResponseUsage,
    RealtimeServerEvent,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseCancelEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreateEvent,
    ResponseCreatedEvent,
    ResponseDoneEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    SessionCreatedEvent,
    SessionUpdateEvent,
    SessionUpdatedEvent,
)
```

### Sessions

Types:

```python
from openai.types.beta.realtime import Session, SessionCreateResponse
```

Methods:

- <code title="post /realtime/sessions">client.beta.realtime.sessions.<a href="./src/openai/resources/beta/realtime/sessions.py">create</a>(\*\*<a href="src/openai/types/beta/realtime/session_create_params.py">params</a>) -> <a href="./src/openai/types/beta/realtime/session_create_response.py">SessionCreateResponse</a></code>

## VectorStores

Types:

```python
from openai.types.beta import (
    AutoFileChunkingStrategyParam,
    FileChunkingStrategy,
    FileChunkingStrategyParam,
    OtherFileChunkingStrategyObject,
    StaticFileChunkingStrategy,
    StaticFileChunkingStrategyObject,
    StaticFileChunkingStrategyParam,
    VectorStore,
    VectorStoreDeleted,
)
```

Methods:

- <code title="post /vector_stores">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">create</a>(\*\*<a href="src/openai/types/beta/vector_store_create_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_store.py">VectorStore</a></code>
- <code title="get /vector_stores/{vector_store_id}">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">retrieve</a>(vector_store_id) -> <a href="./src/openai/types/beta/vector_store.py">VectorStore</a></code>
- <code title="post /vector_stores/{vector_store_id}">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">update</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_store_update_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_store.py">VectorStore</a></code>
- <code title="get /vector_stores">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">list</a>(\*\*<a href="src/openai/types/beta/vector_store_list_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_store.py">SyncCursorPage[VectorStore]</a></code>
- <code title="delete /vector_stores/{vector_store_id}">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">delete</a>(vector_store_id) -> <a href="./src/openai/types/beta/vector_store_deleted.py">VectorStoreDeleted</a></code>

### Files

Types:

```python
from openai.types.beta.vector_stores import VectorStoreFile, VectorStoreFileDeleted
```

Methods:

- <code title="post /vector_stores/{vector_store_id}/files">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">create</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_create_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /vector_stores/{vector_store_id}/files/{file_id}">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">retrieve</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /vector_stores/{vector_store_id}/files">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">list</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_list_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">SyncCursorPage[VectorStoreFile]</a></code>
- <code title="delete /vector_stores/{vector_store_id}/files/{file_id}">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">delete</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_deleted.py">VectorStoreFileDeleted</a></code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">create_and_poll</a>(\*args) -> VectorStoreFile</code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">poll</a>(\*args) -> VectorStoreFile</code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">upload</a>(\*args) -> VectorStoreFile</code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">upload_and_poll</a>(\*args) -> VectorStoreFile</code>

### FileBatches

Types:

```python
from openai.types.beta.vector_stores import VectorStoreFileBatch
```

Methods:

- <code title="post /vector_stores/{vector_store_id}/file_batches">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">create</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_batch_create_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="get /vector_stores/{vector_store_id}/file_batches/{batch_id}">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">retrieve</a>(batch_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="post /vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">cancel</a>(batch_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="get /vector_stores/{vector_store_id}/file_batches/{batch_id}/files">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">list_files</a>(batch_id, \*, vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_batch_list_files_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">SyncCursorPage[VectorStoreFile]</a></code>
- <code>client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">create_and_poll</a>(\*args) -> VectorStoreFileBatch</code>
- <code>client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">poll</a>(\*args) -> VectorStoreFileBatch</code>
- <code>client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">upload_and_poll</a>(\*args) -> VectorStoreFileBatch</code>

## Assistants

Types:

```python
from openai.types.beta import (
    Assistant,
    AssistantDeleted,
    AssistantStreamEvent,
    AssistantTool,
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    MessageStreamEvent,
    RunStepStreamEvent,
    RunStreamEvent,
    ThreadStreamEvent,
)
```

Methods:

- <code title="post /assistants">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">create</a>(\*\*<a href="src/openai/types/beta/assistant_create_params.py">params</a>) -> <a href="./src/openai/types/beta/assistant.py">Assistant</a></code>
- <code title="get /assistants/{assistant_id}">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">retrieve</a>(assistant_id) -> <a href="./src/openai/types/beta/assistant.py">Assistant</a></code>
- <code title="post /assistants/{assistant_id}">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">update</a>(assistant_id, \*\*<a href="src/openai/types/beta/assistant_update_params.py">params</a>) -> <a href="./src/openai/types/beta/assistant.py">Assistant</a></code>
- <code title="get /assistants">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">list</a>(\*\*<a href="src/openai/types/beta/assistant_list_params.py">params</a>) -> <a href="./src/openai/types/beta/assistant.py">SyncCursorPage[Assistant]</a></code>
- <code title="delete /assistants/{assistant_id}">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">delete</a>(assistant_id) -> <a href="./src/openai/types/beta/assistant_deleted.py">AssistantDeleted</a></code>

## Threads

Types:

```python
from openai.types.beta import (
    AssistantResponseFormatOption,
    AssistantToolChoice,
    AssistantToolChoiceFunction,
    AssistantToolChoiceOption,
    Thread,
    ThreadDeleted,
)
```

Methods:

- <code title="post /threads">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create</a>(\*\*<a href="src/openai/types/beta/thread_create_params.py">params</a>) -> <a href="./src/openai/types/beta/thread.py">Thread</a></code>
- <code title="get /threads/{thread_id}">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">retrieve</a>(thread_id) -> <a href="./src/openai/types/beta/thread.py">Thread</a></code>
- <code title="post /threads/{thread_id}">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">update</a>(thread_id, \*\*<a href="src/openai/types/beta/thread_update_params.py">params</a>) -> <a href="./src/openai/types/beta/thread.py">Thread</a></code>
- <code title="delete /threads/{thread_id}">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">delete</a>(thread_id) -> <a href="./src/openai/types/beta/thread_deleted.py">ThreadDeleted</a></code>
- <code title="post /threads/runs">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create_and_run</a>(\*\*<a href="src/openai/types/beta/thread_create_and_run_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code>client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create_and_run_poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create_and_run_stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>

### Runs

Types:

```python
from openai.types.beta.threads import RequiredActionFunctionToolCall, Run, RunStatus
```

Methods:

- <code title="post /threads/{thread_id}/runs">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">create</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/run_create_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="get /threads/{thread_id}/runs/{run_id}">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">retrieve</a>(run_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="post /threads/{thread_id}/runs/{run_id}">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">update</a>(run_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/run_update_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="get /threads/{thread_id}/runs">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">list</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/run_list_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">SyncCursorPage[Run]</a></code>
- <code title="post /threads/{thread_id}/runs/{run_id}/cancel">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">cancel</a>(run_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="post /threads/{thread_id}/runs/{run_id}/submit_tool_outputs">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">submit_tool_outputs</a>(run_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/run_submit_tool_outputs_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">create_and_poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">create_and_stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">submit_tool_outputs_and_poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">submit_tool_outputs_stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>

#### Steps

Types:

```python
from openai.types.beta.threads.runs import (
    CodeInterpreterLogs,
    CodeInterpreterOutputImage,
    CodeInterpreterToolCall,
    CodeInterpreterToolCallDelta,
    FileSearchToolCall,
    FileSearchToolCallDelta,
    FunctionToolCall,
    FunctionToolCallDelta,
    MessageCreationStepDetails,
    RunStep,
    RunStepDelta,
    RunStepDeltaEvent,
    RunStepDeltaMessageDelta,
    RunStepInclude,
    ToolCall,
    ToolCallDelta,
    ToolCallDeltaObject,
    ToolCallsStepDetails,
)
```

Methods:

- <code title="get /threads/{thread_id}/runs/{run_id}/steps/{step_id}">client.beta.threads.runs.steps.<a href="./src/openai/resources/beta/threads/runs/steps.py">retrieve</a>(step_id, \*, thread_id, run_id, \*\*<a href="src/openai/types/beta/threads/runs/step_retrieve_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/runs/run_step.py">RunStep</a></code>
- <code title="get /threads/{thread_id}/runs/{run_id}/steps">client.beta.threads.runs.steps.<a href="./src/openai/resources/beta/threads/runs/steps.py">list</a>(run_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/runs/step_list_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/runs/run_step.py">SyncCursorPage[RunStep]</a></code>

### Messages

Types:

```python
from openai.types.beta.threads import (
    Annotation,
    AnnotationDelta,
    FileCitationAnnotation,
    FileCitationDeltaAnnotation,
    FilePathAnnotation,
    FilePathDeltaAnnotation,
    ImageFile,
    ImageFileContentBlock,
    ImageFileDelta,
    ImageFileDeltaBlock,
    ImageURL,
    ImageURLContentBlock,
    ImageURLDelta,
    ImageURLDeltaBlock,
    Message,
    MessageContent,
    MessageContentDelta,
    MessageContentPartParam,
    MessageDeleted,
    MessageDelta,
    MessageDeltaEvent,
    RefusalContentBlock,
    RefusalDeltaBlock,
    Text,
    TextContentBlock,
    TextContentBlockParam,
    TextDelta,
    TextDeltaBlock,
)
```

Methods:

- <code title="post /threads/{thread_id}/messages">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">create</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/message_create_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/message.py">Message</a></code>
- <code title="get /threads/{thread_id}/messages/{message_id}">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">retrieve</a>(message_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/message.py">Message</a></code>
- <code title="post /threads/{thread_id}/messages/{message_id}">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">update</a>(message_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/message_update_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/message.py">Message</a></code>
- <code title="get /threads/{thread_id}/messages">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">list</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/message_list_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/message.py">SyncCursorPage[Message]</a></code>
- <code title="delete /threads/{thread_id}/messages/{message_id}">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">delete</a>(message_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/message_deleted.py">MessageDeleted</a></code>

# Batches

Types:

```python
from openai.types import Batch, BatchError, BatchRequestCounts
```

Methods:

- <code title="post /batches">client.batches.<a href="./src/openai/resources/batches.py">create</a>(\*\*<a href="src/openai/types/batch_create_params.py">params</a>) -> <a href="./src/openai/types/batch.py">Batch</a></code>
- <code title="get /batches/{batch_id}">client.batches.<a href="./src/openai/resources/batches.py">retrieve</a>(batch_id) -> <a href="./src/openai/types/batch.py">Batch</a></code>
- <code title="get /batches">client.batches.<a href="./src/openai/resources/batches.py">list</a>(\*\*<a href="src/openai/types/batch_list_params.py">params</a>) -> <a href="./src/openai/types/batch.py">SyncCursorPage[Batch]</a></code>
- <code title="post /batches/{batch_id}/cancel">client.batches.<a href="./src/openai/resources/batches.py">cancel</a>(batch_id) -> <a href="./src/openai/types/batch.py">Batch</a></code>

# Uploads

Types:

```python
from openai.types import Upload
```

Methods:

- <code title="post /uploads">client.uploads.<a href="./src/openai/resources/uploads/uploads.py">create</a>(\*\*<a href="src/openai/types/upload_create_params.py">params</a>) -> <a href="./src/openai/types/upload.py">Upload</a></code>
- <code title="post /uploads/{upload_id}/cancel">client.uploads.<a href="./src/openai/resources/uploads/uploads.py">cancel</a>(upload_id) -> <a href="./src/openai/types/upload.py">Upload</a></code>
- <code title="post /uploads/{upload_id}/complete">client.uploads.<a href="./src/openai/resources/uploads/uploads.py">complete</a>(upload_id, \*\*<a href="src/openai/types/upload_complete_params.py">params</a>) -> <a href="./src/openai/types/upload.py">Upload</a></code>

## Parts

Types:

```python
from openai.types.uploads import UploadPart
```

Methods:

- <code title="post /uploads/{upload_id}/parts">client.uploads.parts.<a href="./src/openai/resources/uploads/parts.py">create</a>(upload_id, \*\*<a href="src/openai/types/uploads/part_create_params.py">params</a>) -> <a href="./src/openai/types/uploads/upload_part.py">UploadPart</a></code>


================================================
File: /helpers.md
================================================
# Structured Outputs Parsing Helpers

The OpenAI API supports extracting JSON from the model with the `response_format` request param, for more details on the API, see [this guide](https://platform.openai.com/docs/guides/structured-outputs).

The SDK provides a `client.beta.chat.completions.parse()` method which is a wrapper over the `client.chat.completions.create()` that
provides richer integrations with Python specific types & returns a `ParsedChatCompletion` object, which is a subclass of the standard `ChatCompletion` class.

## Auto-parsing response content with Pydantic models

You can pass a pydantic model to the `.parse()` method and the SDK will automatically convert the model
into a JSON schema, send it to the API and parse the response content back into the given model.

```py
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

client = OpenAI()
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed.steps)
    print("answer: ", message.parsed.final_answer)
else:
    print(message.refusal)
```

## Auto-parsing function tool calls

The `.parse()` method will also automatically parse `function` tool calls if:
- You use the `openai.pydantic_function_tool()` helper method
- You mark your tool schema with `"strict": True`

For example:

```py
from enum import Enum
from typing import List, Union
from pydantic import BaseModel
import openai

class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"

class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"

class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="

class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"

class DynamicValue(BaseModel):
    column_name: str

class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]

class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy

client = openai.OpenAI()
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
        },
        {
            "role": "user",
            "content": "look up all my orders in may of last year that were fulfilled but not delivered on time",
        },
    ],
    tools=[
        openai.pydantic_function_tool(Query),
    ],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
print(tool_call.function)
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)
```

### Differences from `.create()`

The `beta.chat.completions.parse()` method imposes some additional restrictions on it's usage that `chat.completions.create()` does not. 

- If the completion completes with `finish_reason` set to `length` or `content_filter`, the `LengthFinishReasonError` / `ContentFilterFinishReasonError` errors will be raised.
- Only strict function tools can be passed, e.g. `{'type': 'function', 'function': {..., 'strict': True}}`

# Streaming Helpers

OpenAI supports streaming responses when interacting with the [Chat Completion](#chat-completions-api) & [Assistant](#assistant-streaming-api) APIs.

## Chat Completions API

The SDK provides a `.beta.chat.completions.stream()` method that wraps the `.chat.completions.create(stream=True)` stream providing a more granular event API & automatic accumulation of each delta.

It also supports all aforementioned [parsing helpers](#parsing-helpers).

Unlike `.create(stream=True)`, the `.stream()` method requires usage within a context manager to prevent accidental leakage of the response:

```py
from openai import AsyncOpenAI

client = AsyncOpenAI()

async with client.beta.chat.completions.stream(
    model='gpt-4o-2024-08-06',
    messages=[...],
) as stream:
    async for event in stream:
        if event.type == 'content.delta':
            print(event.content, flush=True, end='')
```

When the context manager is entered, a `ChatCompletionStream` / `AsyncChatCompletionStream` instance is returned which, like `.create(stream=True)` is an iterator in the sync client and an async iterator in the async client. The full list of events that are yielded by the iterator are outlined [below](#chat-completions-events).

When the context manager exits, the response will be closed, however the `stream` instance is still available outside
the context manager.

### Chat Completions Events

These events allow you to track the progress of the chat completion generation, access partial results, and handle different aspects of the stream separately.

Below is a list of the different event types you may encounter:

#### ChunkEvent

Emitted for every chunk received from the API.

- `type`: `"chunk"`
- `chunk`: The raw `ChatCompletionChunk` object received from the API
- `snapshot`: The current accumulated state of the chat completion

#### ContentDeltaEvent

Emitted for every chunk containing new content.

- `type`: `"content.delta"`
- `delta`: The new content string received in this chunk
- `snapshot`: The accumulated content so far
- `parsed`: The partially parsed content (if applicable)

#### ContentDoneEvent

Emitted when the content generation is complete. May be fired multiple times if there are multiple choices.

- `type`: `"content.done"`
- `content`: The full generated content
- `parsed`: The fully parsed content (if applicable)

#### RefusalDeltaEvent

Emitted when a chunk contains part of a content refusal.

- `type`: `"refusal.delta"`
- `delta`: The new refusal content string received in this chunk
- `snapshot`: The accumulated refusal content string so far

#### RefusalDoneEvent

Emitted when the refusal content is complete.

- `type`: `"refusal.done"`
- `refusal`: The full refusal content

#### FunctionToolCallArgumentsDeltaEvent

Emitted when a chunk contains part of a function tool call's arguments.

- `type`: `"tool_calls.function.arguments.delta"`
- `name`: The name of the function being called
- `index`: The index of the tool call
- `arguments`: The accumulated raw JSON string of arguments
- `parsed_arguments`: The partially parsed arguments object
- `arguments_delta`: The new JSON string fragment received in this chunk

#### FunctionToolCallArgumentsDoneEvent

Emitted when a function tool call's arguments are complete.

- `type`: `"tool_calls.function.arguments.done"`
- `name`: The name of the function being called
- `index`: The index of the tool call
- `arguments`: The full raw JSON string of arguments
- `parsed_arguments`: The fully parsed arguments object. If you used `openai.pydantic_function_tool()` this will be an instance of the given model.

#### LogprobsContentDeltaEvent

Emitted when a chunk contains new content [log probabilities](https://cookbook.openai.com/examples/using_logprobs).

- `type`: `"logprobs.content.delta"`
- `content`: A list of the new log probabilities received in this chunk
- `snapshot`: A list of the accumulated log probabilities so far

#### LogprobsContentDoneEvent

Emitted when all content [log probabilities](https://cookbook.openai.com/examples/using_logprobs) have been received.

- `type`: `"logprobs.content.done"`
- `content`: The full list of token log probabilities for the content

#### LogprobsRefusalDeltaEvent

Emitted when a chunk contains new refusal [log probabilities](https://cookbook.openai.com/examples/using_logprobs).

- `type`: `"logprobs.refusal.delta"`
- `refusal`: A list of the new log probabilities received in this chunk
- `snapshot`: A list of the accumulated log probabilities so far

#### LogprobsRefusalDoneEvent

Emitted when all refusal [log probabilities](https://cookbook.openai.com/examples/using_logprobs) have been received.

- `type`: `"logprobs.refusal.done"`
- `refusal`: The full list of token log probabilities for the refusal

### Chat Completions stream methods

A handful of helper methods are provided on the stream class for additional convenience,

**`.get_final_completion()`**

Returns the accumulated `ParsedChatCompletion` object

```py
async with client.beta.chat.completions.stream(...) as stream:
    ...

completion = await stream.get_final_completion()
print(completion.choices[0].message)
```

**`.until_done()`**

If you want to wait for the stream to complete, you can use the `.until_done()` method.

```py
async with client.beta.chat.completions.stream(...) as stream:
    await stream.until_done()
    # stream is now finished
```

## Assistant Streaming API

OpenAI supports streaming responses from Assistants. The SDK provides convenience wrappers around the API
so you can subscribe to the types of events you are interested in as well as receive accumulated responses.

More information can be found in the documentation: [Assistant Streaming](https://platform.openai.com/docs/assistants/overview?lang=python)

#### An example of creating a run and subscribing to some events

You can subscribe to events by creating an event handler class and overloading the relevant event handlers.

```python
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta

client = openai.OpenAI()

# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):
  @override
  def on_text_created(self, text: Text) -> None:
    print(f"\nassistant > ", end="", flush=True)

  @override
  def on_text_delta(self, delta: TextDelta, snapshot: Text):
    print(delta.value, end="", flush=True)

  @override
  def on_tool_call_created(self, tool_call: ToolCall):
    print(f"\nassistant > {tool_call.type}\n", flush=True)

  @override
  def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall):
    if delta.type == "code_interpreter" and delta.code_interpreter:
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)

# Then, we use the `stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.

with client.beta.threads.runs.stream(
  thread_id="thread_id",
  assistant_id="assistant_id",
  event_handler=EventHandler(),
) as stream:
  stream.until_done()
```

#### An example of iterating over events

You can also iterate over all the streamed events.

```python
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id
) as stream:
    for event in stream:
        # Print the text from text delta events
        if event.event == "thread.message.delta" and event.data.delta.content:
            print(event.data.delta.content[0].text)
```

#### An example of iterating over text

You can also iterate over just the text deltas received

```python
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id
) as stream:
    for text in stream.text_deltas:
        print(text)
```

### Creating Streams

There are three helper methods for creating streams:

```python
client.beta.threads.runs.stream()
```

This method can be used to start and stream the response to an existing run with an associated thread
that is already populated with messages.

```python
client.beta.threads.create_and_run_stream()
```

This method can be used to add a message to a thread, start a run and then stream the response.

```python
client.beta.threads.runs.submit_tool_outputs_stream()
```

This method can be used to submit a tool output to a run waiting on the output and start a stream.

### Assistant Events

The assistant API provides events you can subscribe to for the following events.

```python
def on_event(self, event: AssistantStreamEvent)
```

This allows you to subscribe to all the possible raw events sent by the OpenAI streaming API.
In many cases it will be more convenient to subscribe to a more specific set of events for your use case.

More information on the types of events can be found here: [Events](https://platform.openai.com/docs/api-reference/assistants-streaming/events)

```python
def on_run_step_created(self, run_step: RunStep)
def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep)
def on_run_step_done(self, run_step: RunStep)
```

These events allow you to subscribe to the creation, delta and completion of a RunStep.

For more information on how Runs and RunSteps work see the documentation [Runs and RunSteps](https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps)

```python
def on_message_created(self, message: Message)
def on_message_delta(self, delta: MessageDelta, snapshot: Message)
def on_message_done(self, message: Message)
```

This allows you to subscribe to Message creation, delta and completion events. Messages can contain
different types of content that can be sent from a model (and events are available for specific content types).
For convenience, the delta event includes both the incremental update and an accumulated snapshot of the content.

More information on messages can be found
on in the documentation page [Message](https://platform.openai.com/docs/api-reference/messages/object).

```python
def on_text_created(self, text: Text)
def on_text_delta(self, delta: TextDelta, snapshot: Text)
def on_text_done(self, text: Text)
```

These events allow you to subscribe to the creation, delta and completion of a Text content (a specific type of message).
For convenience, the delta event includes both the incremental update and an accumulated snapshot of the content.

```python
def on_image_file_done(self, image_file: ImageFile)
```

Image files are not sent incrementally so an event is provided for when a image file is available.

```python
def on_tool_call_created(self, tool_call: ToolCall)
def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall)
def on_tool_call_done(self, tool_call: ToolCall)
```

These events allow you to subscribe to events for the creation, delta and completion of a ToolCall.

More information on tools can be found here [Tools](https://platform.openai.com/docs/assistants/tools)

```python
def on_end(self)
```

The last event send when a stream ends.

```python
def on_timeout(self)
```

This event is triggered if the request times out.

```python
def on_exception(self, exception: Exception)
```

This event is triggered if an exception occurs during streaming.

### Assistant Methods

The assistant streaming object also provides a few methods for convenience:

```python
def current_event() -> AssistantStreamEvent | None
def current_run() -> Run | None
def current_message_snapshot() -> Message | None
def current_run_step_snapshot() -> RunStep | None
```

These methods are provided to allow you to access additional context from within event handlers. In many cases
the handlers should include all the information you need for processing, but if additional context is required it
can be accessed.

Note: There is not always a relevant context in certain situations (these will be `None` in those cases).

```python
def get_final_run(self) -> Run
def get_final_run_steps(self) -> List[RunStep]
def get_final_messages(self) -> List[Message]
```

These methods are provided for convenience to collect information at the end of a stream. Calling these events
will trigger consumption of the stream until completion and then return the relevant accumulated objects.

# Polling Helpers

When interacting with the API some actions such as starting a Run and adding files to vector stores are asynchronous and take time to complete.
The SDK includes helper functions which will poll the status until it reaches a terminal state and then return the resulting object.
If an API method results in an action which could benefit from polling there will be a corresponding version of the
method ending in `_and_poll`.

All methods also allow you to set the polling frequency, how often the API is checked for an update, via a function argument (`poll_interval_ms`).

The polling methods are:

```python
client.beta.threads.create_and_run_poll(...)
client.beta.threads.runs.create_and_poll(...)
client.beta.threads.runs.submit_tool_outputs_and_poll(...)
client.beta.vector_stores.files.upload_and_poll(...)
client.beta.vector_stores.files.create_and_poll(...)
client.beta.vector_stores.file_batches.create_and_poll(...)
client.beta.vector_stores.file_batches.upload_and_poll(...)
```


================================================
File: /mypy.ini
================================================
[mypy]
pretty = True
show_error_codes = True

# Exclude _files.py and _logs.py because mypy isn't smart enough to apply
# the correct type narrowing and as this is an internal module
# it's fine to just use Pyright.
#
# We also exclude our `tests` as mypy doesn't always infer
# types correctly and Pyright will still catch any type errors.

# realtime examples use inline `uv` script dependencies
# which means it can't be type checked
exclude = ^(src/openai/_files\.py|_dev/.*\.py|tests/.*|src/openai/_utils/_logs\.py|examples/realtime/audio_util\.py|examples/realtime/push_to_talk_app\.py)$

strict_equality = True
implicit_reexport = True
check_untyped_defs = True
no_implicit_optional = True

warn_return_any = True
warn_unreachable = True
warn_unused_configs = True

# Turn these options off as it could cause conflicts
# with the Pyright options.
warn_unused_ignores = False
warn_redundant_casts = False

disallow_any_generics = True
disallow_untyped_defs = True
disallow_untyped_calls = True
disallow_subclassing_any = True
disallow_incomplete_defs = True
disallow_untyped_decorators = True
cache_fine_grained = True

# By default, mypy reports an error if you assign a value to the result
# of a function call that doesn't return anything. We do this in our test
# cases:
# ```
# result = ...
# assert result is None
# ```
# Changing this codegen to make mypy happy would increase complexity
# and would not be worth it.
disable_error_code = func-returns-value

# https://github.com/python/mypy/issues/12162
[mypy.overrides]
module = "black.files.*"
ignore_errors = true
ignore_missing_imports = true


================================================
File: /noxfile.py
================================================
import nox


@nox.session(reuse_venv=True, name="test-pydantic-v1")
def test_pydantic_v1(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.install("pydantic<2")

    session.run("pytest", "--showlocals", "--ignore=tests/functional", *session.posargs)


================================================
File: /pyproject.toml
================================================
[project]
name = "openai"
version = "1.59.2"
description = "The official Python library for the openai API"
dynamic = ["readme"]
license = "Apache-2.0"
authors = [
{ name = "OpenAI", email = "support@openai.com" },
]
dependencies = [
    "httpx>=0.23.0, <1",
    "pydantic>=1.9.0, <3",
    "typing-extensions>=4.11, <5",
    "anyio>=3.5.0, <5",
    "distro>=1.7.0, <2",
    "sniffio",
    "tqdm > 4",
    "jiter>=0.4.0, <1",
]
requires-python = ">= 3.8"
classifiers = [
  "Typing :: Typed",
  "Intended Audience :: Developers",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Operating System :: OS Independent",
  "Operating System :: POSIX",
  "Operating System :: MacOS",
  "Operating System :: POSIX :: Linux",
  "Operating System :: Microsoft :: Windows",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "License :: OSI Approved :: Apache Software License"
]

[project.urls]
Homepage = "https://github.com/openai/openai-python"
Repository = "https://github.com/openai/openai-python"

[project.scripts]
openai = "openai.cli:main"

[project.optional-dependencies]
realtime = ["websockets >= 13, < 15"]
datalib = ["numpy >= 1", "pandas >= 1.2.3", "pandas-stubs >= 1.1.0.11"]

[tool.rye]
managed = true
# version pins are in requirements-dev.lock
dev-dependencies = [
    "pyright>=1.1.359",
    "mypy",
    "respx",
    "pytest",
    "pytest-asyncio",
    "ruff",
    "time-machine",
    "nox",
    "dirty-equals>=0.6.0",
    "importlib-metadata>=6.7.0",
    "rich>=13.7.1",
    "inline-snapshot >=0.7.0",
    "azure-identity >=1.14.1",
    "types-tqdm > 4",
    "types-pyaudio > 0",
    "trio >=0.22.2",
    "nest_asyncio==1.6.0"

]

[tool.rye.scripts]
format = { chain = [
  "format:ruff",
  "format:docs",
  "fix:ruff",
  # run formatting again to fix any inconsistencies when imports are stripped
  "format:ruff",
]}
"format:docs" = "python scripts/utils/ruffen-docs.py README.md api.md"
"format:ruff" = "ruff format"

"lint" = { chain = [
  "check:ruff",
  "typecheck",
  "check:importable",
]}
"check:ruff" = "ruff check ."
"fix:ruff" = "ruff check --fix ."

"check:importable" = "python -c 'import openai'"

typecheck = { chain = [
  "typecheck:pyright",
  "typecheck:mypy"
]}
"typecheck:pyright" = "pyright"
"typecheck:verify-types" = "pyright --verifytypes openai --ignoreexternal"
"typecheck:mypy" = "mypy ."

[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme"]
build-backend = "hatchling.build"

[tool.hatch.build]
include = [
  "src/*"
]

[tool.hatch.build.targets.wheel]
packages = ["src/openai"]

[tool.hatch.build.targets.sdist]
# Basically everything except hidden files/directories (such as .github, .devcontainers, .python-version, etc)
include = [
  "/*.toml",
  "/*.json",
  "/*.lock",
  "/*.md",
  "/mypy.ini",
  "/noxfile.py",
  "bin/*",
  "examples/*",
  "src/*",
  "tests/*",
]

[tool.hatch.metadata.hooks.fancy-pypi-readme]
content-type = "text/markdown"

[[tool.hatch.metadata.hooks.fancy-pypi-readme.fragments]]
path = "README.md"

[[tool.hatch.metadata.hooks.fancy-pypi-readme.substitutions]]
# replace relative links with absolute links
pattern = '\[(.+?)\]\(((?!https?://)\S+?)\)'
replacement = '[\1](https://github.com/openai/openai-python/tree/main/\g<2>)'

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"
xfail_strict = true
asyncio_mode = "auto"
filterwarnings = [
  "error"
]

[tool.pyright]
# this enables practically every flag given by pyright.
# there are a couple of flags that are still disabled by
# default in strict mode as they are experimental and niche.
typeCheckingMode = "strict"
pythonVersion = "3.8"

exclude = [
    "_dev",
    ".venv",
    ".nox",

    # uses inline `uv` script dependencies
    # which means it can't be type checked
    "examples/realtime/audio_util.py",
    "examples/realtime/push_to_talk_app.py"
]

reportImplicitOverride = true

reportImportCycles = false
reportPrivateUsage = false


[tool.ruff]
line-length = 120
output-format = "grouped"
target-version = "py37"

[tool.ruff.format]
docstring-code-format = true

[tool.ruff.lint]
select = [
  # isort
  "I",
  # bugbear rules
  "B",
  # remove unused imports
  "F401",
  # bare except statements
  "E722",
  # unused arguments
  "ARG",
  # print statements
  "T201",
  "T203",
  # misuse of typing.TYPE_CHECKING
  "TCH004",
  # import rules
  "TID251",
]
ignore = [
  # mutable defaults
  "B006",
]
unfixable = [
  # disable auto fix for print statements
  "T201",
  "T203",
]

[tool.ruff.lint.flake8-tidy-imports.banned-api]
"functools.lru_cache".msg = "This function does not retain type information for the wrapped function's arguments; The `lru_cache` function from `_utils` should be used instead"

[tool.ruff.lint.isort]
length-sort = true
length-sort-straight = true
combine-as-imports = true
extra-standard-library = ["typing_extensions"]
known-first-party = ["openai", "tests"]

[tool.ruff.lint.per-file-ignores]
"bin/**.py" = ["T201", "T203"]
"scripts/**.py" = ["T201", "T203"]
"tests/**.py" = ["T201", "T203"]
"examples/**.py" = ["T201", "T203"]


================================================
File: /release-please-config.json
================================================
{
  "packages": {
    ".": {}
  },
  "$schema": "https://raw.githubusercontent.com/stainless-api/release-please/main/schemas/config.json",
  "include-v-in-tag": true,
  "include-component-in-tag": false,
  "versioning": "prerelease",
  "prerelease": true,
  "bump-minor-pre-major": true,
  "bump-patch-for-minor-pre-major": false,
  "pull-request-header": "Automated Release PR",
  "pull-request-title-pattern": "release: ${version}",
  "changelog-sections": [
    {
      "type": "feat",
      "section": "Features"
    },
    {
      "type": "fix",
      "section": "Bug Fixes"
    },
    {
      "type": "perf",
      "section": "Performance Improvements"
    },
    {
      "type": "revert",
      "section": "Reverts"
    },
    {
      "type": "chore",
      "section": "Chores"
    },
    {
      "type": "docs",
      "section": "Documentation"
    },
    {
      "type": "style",
      "section": "Styles"
    },
    {
      "type": "refactor",
      "section": "Refactors"
    },
    {
      "type": "test",
      "section": "Tests",
      "hidden": true
    },
    {
      "type": "build",
      "section": "Build System"
    },
    {
      "type": "ci",
      "section": "Continuous Integration",
      "hidden": true
    }
  ],
  "release-type": "python",
  "extra-files": [
    "src/openai/_version.py"
  ]
}

================================================
File: /requirements-dev.lock
================================================
# generated by rye
# use `rye lock` or `rye sync` to update this lockfile
#
# last locked with the following flags:
#   pre: false
#   features: []
#   all-features: true
#   with-sources: false
#   generate-hashes: false

-e file:.
annotated-types==0.6.0
    # via pydantic
anyio==4.1.0
    # via httpx
    # via openai
argcomplete==3.1.2
    # via nox
asttokens==2.4.1
    # via inline-snapshot
attrs==24.2.0
    # via outcome
    # via trio
azure-core==1.31.0
    # via azure-identity
azure-identity==1.19.0
black==24.10.0
    # via inline-snapshot
certifi==2023.7.22
    # via httpcore
    # via httpx
    # via requests
cffi==1.16.0
    # via cryptography
charset-normalizer==3.3.2
    # via requests
click==8.1.7
    # via black
    # via inline-snapshot
colorlog==6.7.0
    # via nox
cryptography==42.0.7
    # via azure-identity
    # via msal
    # via pyjwt
dirty-equals==0.6.0
distlib==0.3.7
    # via virtualenv
distro==1.8.0
    # via openai
exceptiongroup==1.2.2
    # via anyio
    # via pytest
    # via trio
executing==2.1.0
    # via inline-snapshot
filelock==3.12.4
    # via virtualenv
h11==0.14.0
    # via httpcore
httpcore==1.0.2
    # via httpx
httpx==0.25.2
    # via openai
    # via respx
idna==3.4
    # via anyio
    # via httpx
    # via requests
    # via trio
importlib-metadata==7.0.0
iniconfig==2.0.0
    # via pytest
inline-snapshot==0.10.2
jiter==0.5.0
    # via openai
markdown-it-py==3.0.0
    # via rich
mdurl==0.1.2
    # via markdown-it-py
msal==1.31.0
    # via azure-identity
    # via msal-extensions
msal-extensions==1.2.0
    # via azure-identity
mypy==1.13.0
mypy-extensions==1.0.0
    # via black
    # via mypy
nest-asyncio==1.6.0
nodeenv==1.8.0
    # via pyright
nox==2023.4.22
numpy==1.26.3
    # via openai
    # via pandas
    # via pandas-stubs
outcome==1.3.0.post0
    # via trio
packaging==23.2
    # via black
    # via nox
    # via pytest
pandas==2.1.4
    # via openai
pandas-stubs==2.1.4.231227
    # via openai
pathspec==0.12.1
    # via black
platformdirs==3.11.0
    # via black
    # via virtualenv
pluggy==1.5.0
    # via pytest
portalocker==2.10.1
    # via msal-extensions
pycparser==2.22
    # via cffi
pydantic==2.10.3
    # via openai
pydantic-core==2.27.1
    # via pydantic
pygments==2.18.0
    # via rich
pyjwt==2.8.0
    # via msal
pyright==1.1.390
pytest==8.3.3
    # via pytest-asyncio
pytest-asyncio==0.24.0
python-dateutil==2.8.2
    # via pandas
    # via time-machine
pytz==2023.3.post1
    # via dirty-equals
    # via pandas
requests==2.31.0
    # via azure-core
    # via msal
respx==0.20.2
rich==13.7.1
    # via inline-snapshot
ruff==0.6.9
setuptools==68.2.2
    # via nodeenv
six==1.16.0
    # via asttokens
    # via azure-core
    # via python-dateutil
sniffio==1.3.0
    # via anyio
    # via httpx
    # via openai
    # via trio
sortedcontainers==2.4.0
    # via trio
time-machine==2.9.0
toml==0.10.2
    # via inline-snapshot
tomli==2.0.2
    # via black
    # via mypy
    # via pytest
tqdm==4.66.5
    # via openai
trio==0.27.0
types-pyaudio==0.2.16.20240516
types-pytz==2024.2.0.20241003
    # via pandas-stubs
types-toml==0.10.8.20240310
    # via inline-snapshot
types-tqdm==4.66.0.20240417
typing-extensions==4.12.2
    # via azure-core
    # via azure-identity
    # via black
    # via mypy
    # via openai
    # via pydantic
    # via pydantic-core
    # via pyright
tzdata==2024.1
    # via pandas
urllib3==2.2.1
    # via requests
virtualenv==20.24.5
    # via nox
websockets==14.1
    # via openai
zipp==3.17.0
    # via importlib-metadata


================================================
File: /requirements.lock
================================================
# generated by rye
# use `rye lock` or `rye sync` to update this lockfile
#
# last locked with the following flags:
#   pre: false
#   features: []
#   all-features: true
#   with-sources: false
#   generate-hashes: false

-e file:.
annotated-types==0.6.0
    # via pydantic
anyio==4.1.0
    # via httpx
    # via openai
certifi==2023.7.22
    # via httpcore
    # via httpx
distro==1.8.0
    # via openai
exceptiongroup==1.2.2
    # via anyio
h11==0.14.0
    # via httpcore
httpcore==1.0.2
    # via httpx
httpx==0.25.2
    # via openai
idna==3.4
    # via anyio
    # via httpx
jiter==0.6.1
    # via openai
numpy==2.0.2
    # via openai
    # via pandas
    # via pandas-stubs
pandas==2.2.3
    # via openai
pandas-stubs==2.2.2.240807
    # via openai
pydantic==2.10.3
    # via openai
pydantic-core==2.27.1
    # via pydantic
python-dateutil==2.9.0.post0
    # via pandas
pytz==2024.1
    # via pandas
six==1.16.0
    # via python-dateutil
sniffio==1.3.0
    # via anyio
    # via httpx
    # via openai
tqdm==4.66.5
    # via openai
types-pytz==2024.2.0.20241003
    # via pandas-stubs
typing-extensions==4.12.2
    # via openai
    # via pydantic
    # via pydantic-core
tzdata==2024.1
    # via pandas
websockets==14.1
    # via openai


================================================
File: /.python-version
================================================
3.9.18


================================================
File: /.release-please-manifest.json
================================================
{
  ".": "1.59.2"
}

================================================
File: /.stats.yml
================================================
configured_endpoints: 69
openapi_spec_url: https://storage.googleapis.com/stainless-sdk-openapi-specs/openai-a39aca84ed97ebafb707ebd5221e2787c5a42ff3d98f2ffaea8a0dcd84cbcbcb.yml


================================================
File: /bin/check-release-environment
================================================
#!/usr/bin/env bash

errors=()

if [ -z "${STAINLESS_API_KEY}" ]; then
  errors+=("The STAINLESS_API_KEY secret has not been set. Please contact Stainless for an API key & set it in your organization secrets on GitHub.")
fi

if [ -z "${PYPI_TOKEN}" ]; then
  errors+=("The OPENAI_PYPI_TOKEN secret has not been set. Please set it in either this repository's secrets or your organization secrets.")
fi

lenErrors=${#errors[@]}

if [[ lenErrors -gt 0 ]]; then
  echo -e "Found the following errors in the release environment:\n"

  for error in "${errors[@]}"; do
    echo -e "- $error\n"
  done

  exit 1
fi

echo "The environment is ready to push releases!"


================================================
File: /bin/publish-pypi
================================================
#!/usr/bin/env bash

set -eux
mkdir -p dist
rye build --clean
# Patching importlib-metadata version until upstream library version is updated
# https://github.com/pypa/twine/issues/977#issuecomment-2189800841
"$HOME/.rye/self/bin/python3" -m pip install 'importlib-metadata==7.2.1'
rye publish --yes --token=$PYPI_TOKEN


================================================
File: /examples/assistant.py
================================================
import openai

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI()

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
)

print("Run completed with status: " + run.status)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    print("messages: ")
    for message in messages:
        assert message.content[0].type == "text"
        print({"role": message.role, "message": message.content[0].text.value})

    client.beta.assistants.delete(assistant.id)


================================================
File: /examples/assistant_stream.py
================================================
import openai

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI()

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
)

print("starting run stream")

stream = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
    stream=True,
)

for event in stream:
    print(event.model_dump_json(indent=2, exclude_unset=True))

client.beta.assistants.delete(assistant.id)


================================================
File: /examples/assistant_stream_helpers.py
================================================
from __future__ import annotations

from typing_extensions import override

import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta


class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event: AssistantStreamEvent) -> None:
        if event.event == "thread.run.step.created":
            details = event.data.step_details
            if details.type == "tool_calls":
                print("Generating code to interpret:\n\n```py")
        elif event.event == "thread.message.created":
            print("\nResponse:\n")

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        print(delta.value, end="", flush=True)

    @override
    def on_run_step_done(self, run_step: RunStep) -> None:
        details = run_step.step_details
        if details.type == "tool_calls":
            for tool in details.tool_calls:
                if tool.type == "code_interpreter":
                    print("\n```\nExecuting code...")

    @override
    def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
        details = delta.step_details
        if details is not None and details.type == "tool_calls":
            for tool in details.tool_calls or []:
                if tool.type == "code_interpreter" and tool.code_interpreter and tool.code_interpreter.input:
                    print(tool.code_interpreter.input, end="", flush=True)


def main() -> None:
    client = openai.OpenAI()

    assistant = client.beta.assistants.create(
        name="Math Tutor",
        instructions="You are a personal math tutor. Write and run code to answer math questions.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
    )

    try:
        question = "I need to solve the equation `3x + 11 = 14`. Can you help me?"

        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                },
            ]
        )
        print(f"Question: {question}\n")

        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()
            print()
    finally:
        client.beta.assistants.delete(assistant.id)


main()


================================================
File: /examples/async_demo.py
================================================
#!/usr/bin/env -S poetry run python

import asyncio

from openai import AsyncOpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI()


async def main() -> None:
    stream = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Say this is a test",
        stream=True,
    )
    async for completion in stream:
        print(completion.choices[0].text, end="")
    print()


asyncio.run(main())


================================================
File: /examples/audio.py
================================================
#!/usr/bin/env rye run python

import time
from pathlib import Path

from openai import OpenAI

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"


def main() -> None:
    stream_to_speakers()

    # Create text-to-speech audio file
    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input="the quick brown fox jumped over the lazy dogs",
    ) as response:
        response.stream_to_file(speech_file_path)

    # Create transcription from audio file
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=speech_file_path,
    )
    print(transcription.text)

    # Create translation from audio file
    translation = openai.audio.translations.create(
        model="whisper-1",
        file=speech_file_path,
    )
    print(translation.text)


def stream_to_speakers() -> None:
    import pyaudio

    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    start_time = time.time()

    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input="""I see skies of blue and clouds of white
                The bright blessed days, the dark sacred nights
                And I think to myself
                What a wonderful world""",
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        for chunk in response.iter_bytes(chunk_size=1024):
            player_stream.write(chunk)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")


if __name__ == "__main__":
    main()


================================================
File: /examples/azure.py
================================================
from openai import AzureOpenAI

# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2023-07-01-preview"

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())


deployment_client = AzureOpenAI(
    api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-resource.azure.openai.com/",
    # Navigate to the Azure OpenAI Studio to deploy a model.
    azure_deployment="deployment-name",  # e.g. gpt-35-instant
)

completion = deployment_client.chat.completions.create(
    model="<ignored>",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())


================================================
File: /examples/azure_ad.py
================================================
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from openai import AzureOpenAI

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")


# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2023-07-01-preview"

# https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
endpoint = "https://my-resource.openai.azure.com"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())


================================================
File: /examples/demo.py
================================================
#!/usr/bin/env -S poetry run python

from openai import OpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI()

# Non-streaming:
print("----- standard request -----")
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        },
    ],
)
print(completion.choices[0].message.content)

# Streaming:
print("----- streaming request -----")
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue

    print(chunk.choices[0].delta.content, end="")
print()

# Response headers:
print("----- custom response headers test -----")
response = client.chat.completions.with_raw_response.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
)
completion = response.parse()
print(response.request_id)
print(completion.choices[0].message.content)


================================================
File: /examples/generate_file.sh
================================================
# generate a text file with random data for testing file uploads
wanted_size=$((1024*2048*512))
file_size=$(( ((wanted_size/12)+1)*12 ))
read_size=$((file_size*3/4))

echo "wanted=$wanted_size file=$file_size read=$read_size"

dd if=/dev/urandom bs=$read_size count=1 | base64 > /tmp/small_test_file.txt

truncate -s "$wanted_size" /tmp/big_test_file.txt 


================================================
File: /examples/module_client.py
================================================
import openai

# will default to `os.environ['OPENAI_API_KEY']` if not explicitly set
openai.api_key = "..."

# all client options can be configured just like the `OpenAI` instantiation counterpart
openai.base_url = "https://..."
openai.default_headers = {"x-foo": "true"}

# all API calls work in the exact same fashion as well
stream = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)

print()


================================================
File: /examples/parsing.py
================================================
from typing import List

import rich
from pydantic import BaseModel

from openai import OpenAI


class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str


client = OpenAI()

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
)

message = completion.choices[0].message
if message.parsed:
    rich.print(message.parsed.steps)

    print("answer: ", message.parsed.final_answer)
else:
    print(message.refusal)


================================================
File: /examples/parsing_stream.py
================================================
from typing import List

import rich
from pydantic import BaseModel

from openai import OpenAI


class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str


client = OpenAI()

with client.beta.chat.completions.stream(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
) as stream:
    for event in stream:
        if event.type == "content.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "content.done":
            print("\n")
            if event.parsed is not None:
                print(f"answer: {event.parsed.final_answer}")
        elif event.type == "refusal.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "refusal.done":
            print()

print("---------------")
rich.print(stream.get_final_completion())


================================================
File: /examples/parsing_tools.py
================================================
from enum import Enum
from typing import List, Union

import rich
from pydantic import BaseModel

import openai
from openai import OpenAI


class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"


class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"


class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="


class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class DynamicValue(BaseModel):
    column_name: str


class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]


class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy


client = OpenAI()

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
        },
        {
            "role": "user",
            "content": "look up all my orders in november of last year that were fulfilled but not delivered on time",
        },
    ],
    tools=[
        openai.pydantic_function_tool(Query),
    ],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
rich.print(tool_call.function)
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)


================================================
File: /examples/parsing_tools_stream.py
================================================
from __future__ import annotations

import rich
from pydantic import BaseModel

import openai
from openai import OpenAI


class GetWeather(BaseModel):
    city: str
    country: str


client = OpenAI()


with client.beta.chat.completions.stream(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "user",
            "content": "What's the weather like in SF and New York?",
        },
    ],
    tools=[
        # because we're using `.parse_stream()`, the returned tool calls
        # will be automatically deserialized into this `GetWeather` type
        openai.pydantic_function_tool(GetWeather, name="get_weather"),
    ],
    parallel_tool_calls=True,
) as stream:
    for event in stream:
        if event.type == "tool_calls.function.arguments.delta" or event.type == "tool_calls.function.arguments.done":
            rich.get_console().print(event, width=80)

print("----\n")
rich.print(stream.get_final_completion())


================================================
File: /examples/picture.py
================================================
#!/usr/bin/env python

from openai import OpenAI

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()

prompt = "An astronaut lounging in a tropical resort in space, pixel art"
model = "dall-e-3"


def main() -> None:
    # Generate an image based on the prompt
    response = openai.images.generate(prompt=prompt, model=model)

    # Prints response containing a URL link to image
    print(response)


if __name__ == "__main__":
    main()


================================================
File: /examples/streaming.py
================================================
#!/usr/bin/env -S poetry run python

import asyncio

from openai import OpenAI, AsyncOpenAI

# This script assumes you have the OPENAI_API_KEY environment variable set to a valid OpenAI API key.
#
# You can run this script from the root directory like so:
# `python examples/streaming.py`


def sync_main() -> None:
    client = OpenAI()
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="1,2,3,",
        max_tokens=5,
        temperature=0,
        stream=True,
    )

    # You can manually control iteration over the response
    first = next(response)
    print(f"got response data: {first.to_json()}")

    # Or you could automatically iterate through all of data.
    # Note that the for loop will not exit until *all* of the data has been processed.
    for data in response:
        print(data.to_json())


async def async_main() -> None:
    client = AsyncOpenAI()
    response = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="1,2,3,",
        max_tokens=5,
        temperature=0,
        stream=True,
    )

    # You can manually control iteration over the response.
    # In Python 3.10+ you can also use the `await anext(response)` builtin instead
    first = await response.__anext__()
    print(f"got response data: {first.to_json()}")

    # Or you could automatically iterate through all of data.
    # Note that the for loop will not exit until *all* of the data has been processed.
    async for data in response:
        print(data.to_json())


sync_main()

asyncio.run(async_main())


================================================
File: /examples/uploads.py
================================================
import sys
from pathlib import Path

import rich

from openai import OpenAI

# generate this file using `./generate_file.sh`
file = Path("/tmp/big_test_file.txt")

client = OpenAI()


def from_disk() -> None:
    print("uploading file from disk")

    upload = client.uploads.upload_file_chunked(
        file=file,
        mime_type="txt",
        purpose="batch",
    )
    rich.print(upload)


def from_in_memory() -> None:
    print("uploading file from memory")

    # read the data into memory ourselves to simulate
    # it coming from somewhere else
    data = file.read_bytes()
    filename = "my_file.txt"

    upload = client.uploads.upload_file_chunked(
        file=data,
        filename=filename,
        bytes=len(data),
        mime_type="txt",
        purpose="batch",
    )
    rich.print(upload)


if "memory" in sys.argv:
    from_in_memory()
else:
    from_disk()


================================================
File: /examples/.keep
================================================
File generated from our OpenAPI spec by Stainless.

This directory can be used to store example files demonstrating usage of this SDK.
It is ignored by Stainless code generation and its content (other than this keep file) won't be touched.

================================================
File: /examples/realtime/audio_util.py
================================================
from __future__ import annotations

import io
import base64
import asyncio
import threading
from typing import Callable, Awaitable

import numpy as np
import pyaudio
import sounddevice as sd
from pydub import AudioSegment

from openai.resources.beta.realtime.realtime import AsyncRealtimeConnection

CHUNK_LENGTH_S = 0.05  # 100ms
SAMPLE_RATE = 24000
FORMAT = pyaudio.paInt16
CHANNELS = 1

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false


def audio_to_pcm16_base64(audio_bytes: bytes) -> bytes:
    # load the audio file from the byte stream
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    print(f"Loaded audio: {audio.frame_rate=} {audio.channels=} {audio.sample_width=} {audio.frame_width=}")
    # resample to 24kHz mono pcm16
    pcm_audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(CHANNELS).set_sample_width(2).raw_data
    return pcm_audio


class AudioPlayerAsync:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.stream = sd.OutputStream(
            callback=self.callback,
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.int16,
            blocksize=int(CHUNK_LENGTH_S * SAMPLE_RATE),
        )
        self.playing = False
        self._frame_count = 0

    def callback(self, outdata, frames, time, status):  # noqa
        with self.lock:
            data = np.empty(0, dtype=np.int16)

            # get next item from queue if there is still space in the buffer
            while len(data) < frames and len(self.queue) > 0:
                item = self.queue.pop(0)
                frames_needed = frames - len(data)
                data = np.concatenate((data, item[:frames_needed]))
                if len(item) > frames_needed:
                    self.queue.insert(0, item[frames_needed:])

            self._frame_count += len(data)

            # fill the rest of the frames with zeros if there is no more data
            if len(data) < frames:
                data = np.concatenate((data, np.zeros(frames - len(data), dtype=np.int16)))

        outdata[:] = data.reshape(-1, 1)

    def reset_frame_count(self):
        self._frame_count = 0

    def get_frame_count(self):
        return self._frame_count

    def add_data(self, data: bytes):
        with self.lock:
            # bytes is pcm16 single channel audio data, convert to numpy array
            np_data = np.frombuffer(data, dtype=np.int16)
            self.queue.append(np_data)
            if not self.playing:
                self.start()

    def start(self):
        self.playing = True
        self.stream.start()

    def stop(self):
        self.playing = False
        self.stream.stop()
        with self.lock:
            self.queue = []

    def terminate(self):
        self.stream.close()


async def send_audio_worker_sounddevice(
    connection: AsyncRealtimeConnection,
    should_send: Callable[[], bool] | None = None,
    start_send: Callable[[], Awaitable[None]] | None = None,
):
    sent_audio = False

    device_info = sd.query_devices()
    print(device_info)

    read_size = int(SAMPLE_RATE * 0.02)

    stream = sd.InputStream(
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        dtype="int16",
    )
    stream.start()

    try:
        while True:
            if stream.read_available < read_size:
                await asyncio.sleep(0)
                continue

            data, _ = stream.read(read_size)

            if should_send() if should_send else True:
                if not sent_audio and start_send:
                    await start_send()
                await connection.send(
                    {"type": "input_audio_buffer.append", "audio": base64.b64encode(data).decode("utf-8")}
                )
                sent_audio = True

            elif sent_audio:
                print("Done, triggering inference")
                await connection.send({"type": "input_audio_buffer.commit"})
                await connection.send({"type": "response.create", "response": {}})
                sent_audio = False

            await asyncio.sleep(0)

    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        stream.close()


================================================
File: /examples/realtime/push_to_talk_app.py
================================================
#!/usr/bin/env uv run
####################################################################
# Sample TUI app with a push to talk interface to the Realtime API #
# If you have `uv` installed and the `OPENAI_API_KEY`              #
# environment variable set, you can run this example with just     #
#                                                                  #
# `./examples/realtime/push_to_talk_app.py`                        #
####################################################################
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "textual",
#     "numpy",
#     "pyaudio",
#     "pydub",
#     "sounddevice",
#     "openai[realtime]",
# ]
#
# [tool.uv.sources]
# openai = { path = "../../", editable = true }
# ///
from __future__ import annotations

import base64
import asyncio
from typing import Any, cast
from typing_extensions import override

from textual import events
from audio_util import CHANNELS, SAMPLE_RATE, AudioPlayerAsync
from textual.app import App, ComposeResult
from textual.widgets import Button, Static, RichLog
from textual.reactive import reactive
from textual.containers import Container

from openai import AsyncOpenAI
from openai.types.beta.realtime.session import Session
from openai.resources.beta.realtime.realtime import AsyncRealtimeConnection


class SessionDisplay(Static):
    """A widget that shows the current session ID."""

    session_id = reactive("")

    @override
    def render(self) -> str:
        return f"Session ID: {self.session_id}" if self.session_id else "Connecting..."


class AudioStatusIndicator(Static):
    """A widget that shows the current audio recording status."""

    is_recording = reactive(False)

    @override
    def render(self) -> str:
        status = (
            "🔴 Recording... (Press K to stop)" if self.is_recording else "⚪ Press K to start recording (Q to quit)"
        )
        return status


class RealtimeApp(App[None]):
    CSS = """
        Screen {
            background: #1a1b26;  /* Dark blue-grey background */
        }

        Container {
            border: double rgb(91, 164, 91);
        }

        Horizontal {
            width: 100%;
        }

        #input-container {
            height: 5;  /* Explicit height for input container */
            margin: 1 1;
            padding: 1 2;
        }

        Input {
            width: 80%;
            height: 3;  /* Explicit height for input */
        }

        Button {
            width: 20%;
            height: 3;  /* Explicit height for button */
        }

        #bottom-pane {
            width: 100%;
            height: 82%;  /* Reduced to make room for session display */
            border: round rgb(205, 133, 63);
            content-align: center middle;
        }

        #status-indicator {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        #session-display {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        Static {
            color: white;
        }
    """

    client: AsyncOpenAI
    should_send_audio: asyncio.Event
    audio_player: AudioPlayerAsync
    last_audio_item_id: str | None
    connection: AsyncRealtimeConnection | None
    session: Session | None
    connected: asyncio.Event

    def __init__(self) -> None:
        super().__init__()
        self.connection = None
        self.session = None
        self.client = AsyncOpenAI()
        self.audio_player = AudioPlayerAsync()
        self.last_audio_item_id = None
        self.should_send_audio = asyncio.Event()
        self.connected = asyncio.Event()

    @override
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container():
            yield SessionDisplay(id="session-display")
            yield AudioStatusIndicator(id="status-indicator")
            yield RichLog(id="bottom-pane", wrap=True, highlight=True, markup=True)

    async def on_mount(self) -> None:
        self.run_worker(self.handle_realtime_connection())
        self.run_worker(self.send_mic_audio())

    async def handle_realtime_connection(self) -> None:
        async with self.client.beta.realtime.connect(model="gpt-4o-realtime-preview-2024-10-01") as conn:
            self.connection = conn
            self.connected.set()

            # note: this is the default and can be omitted
            # if you want to manually handle VAD yourself, then set `'turn_detection': None`
            await conn.session.update(session={"turn_detection": {"type": "server_vad"}})

            acc_items: dict[str, Any] = {}

            async for event in conn:
                if event.type == "session.created":
                    self.session = event.session
                    session_display = self.query_one(SessionDisplay)
                    assert event.session.id is not None
                    session_display.session_id = event.session.id
                    continue

                if event.type == "session.updated":
                    self.session = event.session
                    continue

                if event.type == "response.audio.delta":
                    if event.item_id != self.last_audio_item_id:
                        self.audio_player.reset_frame_count()
                        self.last_audio_item_id = event.item_id

                    bytes_data = base64.b64decode(event.delta)
                    self.audio_player.add_data(bytes_data)
                    continue

                if event.type == "response.audio_transcript.delta":
                    try:
                        text = acc_items[event.item_id]
                    except KeyError:
                        acc_items[event.item_id] = event.delta
                    else:
                        acc_items[event.item_id] = text + event.delta

                    # Clear and update the entire content because RichLog otherwise treats each delta as a new line
                    bottom_pane = self.query_one("#bottom-pane", RichLog)
                    bottom_pane.clear()
                    bottom_pane.write(acc_items[event.item_id])
                    continue

    async def _get_connection(self) -> AsyncRealtimeConnection:
        await self.connected.wait()
        assert self.connection is not None
        return self.connection

    async def send_mic_audio(self) -> None:
        import sounddevice as sd  # type: ignore

        sent_audio = False

        device_info = sd.query_devices()
        print(device_info)

        read_size = int(SAMPLE_RATE * 0.02)

        stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype="int16",
        )
        stream.start()

        status_indicator = self.query_one(AudioStatusIndicator)

        try:
            while True:
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                await self.should_send_audio.wait()
                status_indicator.is_recording = True

                data, _ = stream.read(read_size)

                connection = await self._get_connection()
                if not sent_audio:
                    asyncio.create_task(connection.send({"type": "response.cancel"}))
                    sent_audio = True

                await connection.input_audio_buffer.append(audio=base64.b64encode(cast(Any, data)).decode("utf-8"))

                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop()
            stream.close()

    async def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "enter":
            self.query_one(Button).press()
            return

        if event.key == "q":
            self.exit()
            return

        if event.key == "k":
            status_indicator = self.query_one(AudioStatusIndicator)
            if status_indicator.is_recording:
                self.should_send_audio.clear()
                status_indicator.is_recording = False

                if self.session and self.session.turn_detection is None:
                    # The default in the API is that the model will automatically detect when the user has
                    # stopped talking and then start responding itself.
                    #
                    # However if we're in manual `turn_detection` mode then we need to
                    # manually tell the model to commit the audio buffer and start responding.
                    conn = await self._get_connection()
                    await conn.input_audio_buffer.commit()
                    await conn.response.create()
            else:
                self.should_send_audio.set()
                status_indicator.is_recording = True


if __name__ == "__main__":
    app = RealtimeApp()
    app.run()


================================================
File: /scripts/bootstrap
================================================
#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

if [ -f "Brewfile" ] && [ "$(uname -s)" = "Darwin" ]; then
  brew bundle check >/dev/null 2>&1 || {
    echo "==> Installing Homebrew dependencies…"
    brew bundle
  }
fi

echo "==> Installing Python dependencies…"

# experimental uv support makes installations significantly faster
rye config --set-bool behavior.use-uv=true

rye sync


================================================
File: /scripts/format
================================================
#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo "==> Running formatters"
rye run format


================================================
File: /scripts/lint
================================================
#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo "==> Running lints"
rye run lint

echo "==> Making sure it imports"
rye run python -c 'import openai'



================================================
File: /scripts/mock
================================================
#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

if [[ -n "$1" && "$1" != '--'* ]]; then
  URL="$1"
  shift
else
  URL="$(grep 'openapi_spec_url' .stats.yml | cut -d' ' -f2)"
fi

# Check if the URL is empty
if [ -z "$URL" ]; then
  echo "Error: No OpenAPI spec path/url provided or found in .stats.yml"
  exit 1
fi

echo "==> Starting mock server with URL ${URL}"

# Run prism mock on the given spec
if [ "$1" == "--daemon" ]; then
  npm exec --package=@stainless-api/prism-cli@5.8.5 -- prism mock "$URL" &> .prism.log &

  # Wait for server to come online
  echo -n "Waiting for server"
  while ! grep -q "✖  fatal\|Prism is listening" ".prism.log" ; do
    echo -n "."
    sleep 0.1
  done

  if grep -q "✖  fatal" ".prism.log"; then
    cat .prism.log
    exit 1
  fi

  echo
else
  npm exec --package=@stainless-api/prism-cli@5.8.5 -- prism mock "$URL"
fi


================================================
File: /scripts/test
================================================
#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

function prism_is_running() {
  curl --silent "http://localhost:4010" >/dev/null 2>&1
}

kill_server_on_port() {
  pids=$(lsof -t -i tcp:"$1" || echo "")
  if [ "$pids" != "" ]; then
    kill "$pids"
    echo "Stopped $pids."
  fi
}

function is_overriding_api_base_url() {
  [ -n "$TEST_API_BASE_URL" ]
}

if ! is_overriding_api_base_url && ! prism_is_running ; then
  # When we exit this script, make sure to kill the background mock server process
  trap 'kill_server_on_port 4010' EXIT

  # Start the dev server
  ./scripts/mock --daemon
fi

if is_overriding_api_base_url ; then
  echo -e "${GREEN}✔ Running tests against ${TEST_API_BASE_URL}${NC}"
  echo
elif ! prism_is_running ; then
  echo -e "${RED}ERROR:${NC} The test suite will not run without a mock Prism server"
  echo -e "running against your OpenAPI spec."
  echo
  echo -e "To run the server, pass in the path or url of your OpenAPI"
  echo -e "spec to the prism command:"
  echo
  echo -e "  \$ ${YELLOW}npm exec --package=@stoplight/prism-cli@~5.3.2 -- prism mock path/to/your.openapi.yml${NC}"
  echo

  exit 1
else
  echo -e "${GREEN}✔ Mock prism server is running with your OpenAPI spec${NC}"
  echo
fi

echo "==> Running tests"
rye run pytest "$@"

echo "==> Running Pydantic v1 tests"
rye run nox -s test-pydantic-v1 -- "$@"


================================================
File: /scripts/utils/ruffen-docs.py
================================================
# fork of https://github.com/asottile/blacken-docs adapted for ruff
from __future__ import annotations

import re
import sys
import argparse
import textwrap
import contextlib
import subprocess
from typing import Match, Optional, Sequence, Generator, NamedTuple, cast

MD_RE = re.compile(
    r"(?P<before>^(?P<indent> *)```\s*python\n)" r"(?P<code>.*?)" r"(?P<after>^(?P=indent)```\s*$)",
    re.DOTALL | re.MULTILINE,
)
MD_PYCON_RE = re.compile(
    r"(?P<before>^(?P<indent> *)```\s*pycon\n)" r"(?P<code>.*?)" r"(?P<after>^(?P=indent)```.*$)",
    re.DOTALL | re.MULTILINE,
)
PYCON_PREFIX = ">>> "
PYCON_CONTINUATION_PREFIX = "..."
PYCON_CONTINUATION_RE = re.compile(
    rf"^{re.escape(PYCON_CONTINUATION_PREFIX)}( |$)",
)
DEFAULT_LINE_LENGTH = 100


class CodeBlockError(NamedTuple):
    offset: int
    exc: Exception


def format_str(
    src: str,
) -> tuple[str, Sequence[CodeBlockError]]:
    errors: list[CodeBlockError] = []

    @contextlib.contextmanager
    def _collect_error(match: Match[str]) -> Generator[None, None, None]:
        try:
            yield
        except Exception as e:
            errors.append(CodeBlockError(match.start(), e))

    def _md_match(match: Match[str]) -> str:
        code = textwrap.dedent(match["code"])
        with _collect_error(match):
            code = format_code_block(code)
        code = textwrap.indent(code, match["indent"])
        return f'{match["before"]}{code}{match["after"]}'

    def _pycon_match(match: Match[str]) -> str:
        code = ""
        fragment = cast(Optional[str], None)

        def finish_fragment() -> None:
            nonlocal code
            nonlocal fragment

            if fragment is not None:
                with _collect_error(match):
                    fragment = format_code_block(fragment)
                fragment_lines = fragment.splitlines()
                code += f"{PYCON_PREFIX}{fragment_lines[0]}\n"
                for line in fragment_lines[1:]:
                    # Skip blank lines to handle Black adding a blank above
                    # functions within blocks. A blank line would end the REPL
                    # continuation prompt.
                    #
                    # >>> if True:
                    # ...     def f():
                    # ...         pass
                    # ...
                    if line:
                        code += f"{PYCON_CONTINUATION_PREFIX} {line}\n"
                if fragment_lines[-1].startswith(" "):
                    code += f"{PYCON_CONTINUATION_PREFIX}\n"
                fragment = None

        indentation = None
        for line in match["code"].splitlines():
            orig_line, line = line, line.lstrip()
            if indentation is None and line:
                indentation = len(orig_line) - len(line)
            continuation_match = PYCON_CONTINUATION_RE.match(line)
            if continuation_match and fragment is not None:
                fragment += line[continuation_match.end() :] + "\n"
            else:
                finish_fragment()
                if line.startswith(PYCON_PREFIX):
                    fragment = line[len(PYCON_PREFIX) :] + "\n"
                else:
                    code += orig_line[indentation:] + "\n"
        finish_fragment()
        return code

    def _md_pycon_match(match: Match[str]) -> str:
        code = _pycon_match(match)
        code = textwrap.indent(code, match["indent"])
        return f'{match["before"]}{code}{match["after"]}'

    src = MD_RE.sub(_md_match, src)
    src = MD_PYCON_RE.sub(_md_pycon_match, src)
    return src, errors


def format_code_block(code: str) -> str:
    return subprocess.check_output(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--stdin-filename=script.py",
            f"--line-length={DEFAULT_LINE_LENGTH}",
        ],
        encoding="utf-8",
        input=code,
    )


def format_file(
    filename: str,
    skip_errors: bool,
) -> int:
    with open(filename, encoding="UTF-8") as f:
        contents = f.read()
    new_contents, errors = format_str(contents)
    for error in errors:
        lineno = contents[: error.offset].count("\n") + 1
        print(f"{filename}:{lineno}: code block parse error {error.exc}")
    if errors and not skip_errors:
        return 1
    if contents != new_contents:
        print(f"{filename}: Rewriting...")
        with open(filename, "w", encoding="UTF-8") as f:
            f.write(new_contents)
        return 0
    else:
        return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--line-length",
        type=int,
        default=DEFAULT_LINE_LENGTH,
    )
    parser.add_argument(
        "-S",
        "--skip-string-normalization",
        action="store_true",
    )
    parser.add_argument("-E", "--skip-errors", action="store_true")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    retv = 0
    for filename in args.filenames:
        retv |= format_file(filename, skip_errors=args.skip_errors)
    return retv


if __name__ == "__main__":
    raise SystemExit(main())


================================================
File: /src/openai/__init__.py
================================================
# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os as _os
from typing_extensions import override

from . import types
from ._types import NOT_GIVEN, Omit, NoneType, NotGiven, Transport, ProxiesTypes
from ._utils import file_from_path
from ._client import Client, OpenAI, Stream, Timeout, Transport, AsyncClient, AsyncOpenAI, AsyncStream, RequestOptions
from ._models import BaseModel
from ._version import __title__, __version__
from ._response import APIResponse as APIResponse, AsyncAPIResponse as AsyncAPIResponse
from ._constants import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_CONNECTION_LIMITS
from ._exceptions import (
    APIError,
    OpenAIError,
    ConflictError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    LengthFinishReasonError,
    UnprocessableEntityError,
    APIResponseValidationError,
    ContentFilterFinishReasonError,
)
from ._base_client import DefaultHttpxClient, DefaultAsyncHttpxClient
from ._utils._logs import setup_logging as _setup_logging

__all__ = [
    "types",
    "__version__",
    "__title__",
    "NoneType",
    "Transport",
    "ProxiesTypes",
    "NotGiven",
    "NOT_GIVEN",
    "Omit",
    "OpenAIError",
    "APIError",
    "APIStatusError",
    "APITimeoutError",
    "APIConnectionError",
    "APIResponseValidationError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "LengthFinishReasonError",
    "ContentFilterFinishReasonError",
    "Timeout",
    "RequestOptions",
    "Client",
    "AsyncClient",
    "Stream",
    "AsyncStream",
    "OpenAI",
    "AsyncOpenAI",
    "file_from_path",
    "BaseModel",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_CONNECTION_LIMITS",
    "DefaultHttpxClient",
    "DefaultAsyncHttpxClient",
]

from .lib import azure as _azure, pydantic_function_tool as pydantic_function_tool
from .version import VERSION as VERSION
from .lib.azure import AzureOpenAI as AzureOpenAI, AsyncAzureOpenAI as AsyncAzureOpenAI
from .lib._old_api import *
from .lib.streaming import (
    AssistantEventHandler as AssistantEventHandler,
    AsyncAssistantEventHandler as AsyncAssistantEventHandler,
)

_setup_logging()

# Update the __module__ attribute for exported symbols so that
# error messages point to this module instead of the module
# it was originally defined in, e.g.
# openai._exceptions.NotFoundError -> openai.NotFoundError
__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        try:
            __locals[__name].__module__ = "openai"
        except (TypeError, AttributeError):
            # Some of our exported symbols are builtins which we can't set attributes for.
            pass

# ------ Module level client ------
import typing as _t
import typing_extensions as _te

import httpx as _httpx

from ._base_client import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES

api_key: str | None = None

organization: str | None = None

project: str | None = None

base_url: str | _httpx.URL | None = None

timeout: float | Timeout | None = DEFAULT_TIMEOUT

max_retries: int = DEFAULT_MAX_RETRIES

default_headers: _t.Mapping[str, str] | None = None

default_query: _t.Mapping[str, object] | None = None

http_client: _httpx.Client | None = None

_ApiType = _te.Literal["openai", "azure"]

api_type: _ApiType | None = _t.cast(_ApiType, _os.environ.get("OPENAI_API_TYPE"))

api_version: str | None = _os.environ.get("OPENAI_API_VERSION")

azure_endpoint: str | None = _os.environ.get("AZURE_OPENAI_ENDPOINT")

azure_ad_token: str | None = _os.environ.get("AZURE_OPENAI_AD_TOKEN")

azure_ad_token_provider: _azure.AzureADTokenProvider | None = None


class _ModuleClient(OpenAI):
    # Note: we have to use type: ignores here as overriding class members
    # with properties is technically unsafe but it is fine for our use case

    @property  # type: ignore
    @override
    def api_key(self) -> str | None:
        return api_key

    @api_key.setter  # type: ignore
    def api_key(self, value: str | None) -> None:  # type: ignore
        global api_key

        api_key = value

    @property  # type: ignore
    @override
    def organization(self) -> str | None:
        return organization

    @organization.setter  # type: ignore
    def organization(self, value: str | None) -> None:  # type: ignore
        global organization

        organization = value

    @property  # type: ignore
    @override
    def project(self) -> str | None:
        return project

    @project.setter  # type: ignore
    def project(self, value: str | None) -> None:  # type: ignore
        global project

        project = value

    @property
    @override
    def base_url(self) -> _httpx.URL:
        if base_url is not None:
            return _httpx.URL(base_url)

        return super().base_url

    @base_url.setter
    def base_url(self, url: _httpx.URL | str) -> None:
        super().base_url = url  # type: ignore[misc]

    @property  # type: ignore
    @override
    def timeout(self) -> float | Timeout | None:
        return timeout

    @timeout.setter  # type: ignore
    def timeout(self, value: float | Timeout | None) -> None:  # type: ignore
        global timeout

        timeout = value

    @property  # type: ignore
    @override
    def max_retries(self) -> int:
        return max_retries

    @max_retries.setter  # type: ignore
    def max_retries(self, value: int) -> None:  # type: ignore
        global max_retries

        max_retries = value

    @property  # type: ignore
    @override
    def _custom_headers(self) -> _t.Mapping[str, str] | None:
        return default_headers

    @_custom_headers.setter  # type: ignore
    def _custom_headers(self, value: _t.Mapping[str, str] | None) -> None:  # type: ignore
        global default_headers

        default_headers = value

    @property  # type: ignore
    @override
    def _custom_query(self) -> _t.Mapping[str, object] | None:
        return default_query

    @_custom_query.setter  # type: ignore
    def _custom_query(self, value: _t.Mapping[str, object] | None) -> None:  # type: ignore
        global default_query

        default_query = value

    @property  # type: ignore
    @override
    def _client(self) -> _httpx.Client:
        return http_client or super()._client

    @_client.setter  # type: ignore
    def _client(self, value: _httpx.Client) -> None:  # type: ignore
        global http_client

        http_client = value


class _AzureModuleClient(_ModuleClient, AzureOpenAI):  # type: ignore
    ...


class _AmbiguousModuleClientUsageError(OpenAIError):
    def __init__(self) -> None:
        super().__init__(
            "Ambiguous use of module client; please set `openai.api_type` or the `OPENAI_API_TYPE` environment variable to `openai` or `azure`"
        )


def _has_openai_credentials() -> bool:
    return _os.environ.get("OPENAI_API_KEY") is not None


def _has_azure_credentials() -> bool:
    return azure_endpoint is not None or _os.environ.get("AZURE_OPENAI_API_KEY") is not None


def _has_azure_ad_credentials() -> bool:
    return (
        _os.environ.get("AZURE_OPENAI_AD_TOKEN") is not None
        or azure_ad_token is not None
        or azure_ad_token_provider is not None
    )


_client: OpenAI | None = None


def _load_client() -> OpenAI:  # type: ignore[reportUnusedFunction]
    global _client

    if _client is None:
        global api_type, azure_endpoint, azure_ad_token, api_version

        if azure_endpoint is None:
            azure_endpoint = _os.environ.get("AZURE_OPENAI_ENDPOINT")

        if azure_ad_token is None:
            azure_ad_token = _os.environ.get("AZURE_OPENAI_AD_TOKEN")

        if api_version is None:
            api_version = _os.environ.get("OPENAI_API_VERSION")

        if api_type is None:
            has_openai = _has_openai_credentials()
            has_azure = _has_azure_credentials()
            has_azure_ad = _has_azure_ad_credentials()

            if has_openai and (has_azure or has_azure_ad):
                raise _AmbiguousModuleClientUsageError()

            if (azure_ad_token is not None or azure_ad_token_provider is not None) and _os.environ.get(
                "AZURE_OPENAI_API_KEY"
            ) is not None:
                raise _AmbiguousModuleClientUsageError()

            if has_azure or has_azure_ad:
                api_type = "azure"
            else:
                api_type = "openai"

        if api_type == "azure":
            _client = _AzureModuleClient(  # type: ignore
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                azure_ad_token=azure_ad_token,
                azure_ad_token_provider=azure_ad_token_provider,
                organization=organization,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                default_headers=default_headers,
                default_query=default_query,
                http_client=http_client,
            )
            return _client

        _client = _ModuleClient(
            api_key=api_key,
            organization=organization,
            project=project,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
        )
        return _client

    return _client


def _reset_client() -> None:  # type: ignore[reportUnusedFunction]
    global _client

    _client = None


from ._module_client import (
    beta as beta,
    chat as chat,
    audio as audio,
    files as files,
    images as images,
    models as models,
    batches as batches,
    embeddings as embeddings,
    completions as completions,
    fine_tuning as fine_tuning,
    moderations as moderations,
)


================================================
File: /src/openai/__main__.py
================================================
from .cli import main

main()


================================================
File: /src/openai/_client.py
================================================
# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    is_mapping,
    get_async_library,
)
from ._version import __version__
from .resources import files, images, models, batches, embeddings, completions, moderations
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import OpenAIError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.beta import beta
from .resources.chat import chat
from .resources.audio import audio
from .resources.uploads import uploads
from .resources.fine_tuning import fine_tuning

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "OpenAI", "AsyncOpenAI", "Client", "AsyncClient"]


class OpenAI(SyncAPIClient):
    completions: completions.Completions
    chat: chat.Chat
    embeddings: embeddings.Embeddings
    files: files.Files
    images: images.Images
    audio: audio.Audio
    moderations: moderations.Moderations
    models: models.Models
    fine_tuning: fine_tuning.FineTuning
    beta: beta.Beta
    batches: batches.Batches
    uploads: uploads.Uploads
    with_raw_response: OpenAIWithRawResponse
    with_streaming_response: OpenAIWithStreamedResponse

    # client options
    api_key: str
    organization: str | None
    project: str | None

    websocket_base_url: str | httpx.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous openai client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `OPENAI_API_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
            )
        self.api_key = api_key

        if organization is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        if project is None:
            project = os.environ.get("OPENAI_PROJECT_ID")
        self.project = project

        self.websocket_base_url = websocket_base_url

        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url is None:
            base_url = f"https://api.openai.com/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = Stream

        self.completions = completions.Completions(self)
        self.chat = chat.Chat(self)
        self.embeddings = embeddings.Embeddings(self)
        self.files = files.Files(self)
        self.images = images.Images(self)
        self.audio = audio.Audio(self)
        self.moderations = moderations.Moderations(self)
        self.models = models.Models(self)
        self.fine_tuning = fine_tuning.FineTuning(self)
        self.beta = beta.Beta(self)
        self.batches = batches.Batches(self)
        self.uploads = uploads.Uploads(self)
        self.with_raw_response = OpenAIWithRawResponse(self)
        self.with_streaming_response = OpenAIWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            "OpenAI-Project": self.project if self.project is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            organization=organization or self.organization,
            project=project or self.project,
            websocket_base_url=websocket_base_url or self.websocket_base_url,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        data = body.get("error", body) if is_mapping(body) else body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=data)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=data)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=data)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=data)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=data)
        return APIStatusError(err_msg, response=response, body=data)


class AsyncOpenAI(AsyncAPIClient):
    completions: completions.AsyncCompletions
    chat: chat.AsyncChat
    embeddings: embeddings.AsyncEmbeddings
    files: files.AsyncFiles
    images: images.AsyncImages
    audio: audio.AsyncAudio
    moderations: moderations.AsyncModerations
    models: models.AsyncModels
    fine_tuning: fine_tuning.AsyncFineTuning
    beta: beta.AsyncBeta
    batches: batches.AsyncBatches
    uploads: uploads.AsyncUploads
    with_raw_response: AsyncOpenAIWithRawResponse
    with_streaming_response: AsyncOpenAIWithStreamedResponse

    # client options
    api_key: str
    organization: str | None
    project: str | None

    websocket_base_url: str | httpx.URL | None
    """Base URL for WebSocket connections.

    If not specified, the default base URL will be used, with 'wss://' replacing the
    'http://' or 'https://' scheme. For example: 'http://example.com' becomes
    'wss://example.com'
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async openai client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `OPENAI_API_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise OpenAIError(
                "The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable"
            )
        self.api_key = api_key

        if organization is None:
            organization = os.environ.get("OPENAI_ORG_ID")
        self.organization = organization

        if project is None:
            project = os.environ.get("OPENAI_PROJECT_ID")
        self.project = project

        self.websocket_base_url = websocket_base_url

        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url is None:
            base_url = f"https://api.openai.com/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = AsyncStream

        self.completions = completions.AsyncCompletions(self)
        self.chat = chat.AsyncChat(self)
        self.embeddings = embeddings.AsyncEmbeddings(self)
        self.files = files.AsyncFiles(self)
        self.images = images.AsyncImages(self)
        self.audio = audio.AsyncAudio(self)
        self.moderations = moderations.AsyncModerations(self)
        self.models = models.AsyncModels(self)
        self.fine_tuning = fine_tuning.AsyncFineTuning(self)
        self.beta = beta.AsyncBeta(self)
        self.batches = batches.AsyncBatches(self)
        self.uploads = uploads.AsyncUploads(self)
        self.with_raw_response = AsyncOpenAIWithRawResponse(self)
        self.with_streaming_response = AsyncOpenAIWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            "OpenAI-Organization": self.organization if self.organization is not None else Omit(),
            "OpenAI-Project": self.project if self.project is not None else Omit(),
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            organization=organization or self.organization,
            project=project or self.project,
            websocket_base_url=websocket_base_url or self.websocket_base_url,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        data = body.get("error", body) if is_mapping(body) else body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=data)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=data)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=data)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=data)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=data)
        return APIStatusError(err_msg, response=response, body=data)


class OpenAIWithRawResponse:
    def __init__(self, client: OpenAI) -> None:
        self.completions = completions.CompletionsWithRawResponse(client.completions)
        self.chat = chat.ChatWithRawResponse(client.chat)
        self.embeddings = embeddings.EmbeddingsWithRawResponse(client.embeddings)
        self.files = files.FilesWithRawResponse(client.files)
        self.images = images.ImagesWithRawResponse(client.images)
        self.audio = audio.AudioWithRawResponse(client.audio)
        self.moderations = moderations.ModerationsWithRawResponse(client.moderations)
        self.models = models.ModelsWithRawResponse(client.models)
        self.fine_tuning = fine_tuning.FineTuningWithRawResponse(client.fine_tuning)
        self.beta = beta.BetaWithRawResponse(client.beta)
        self.batches = batches.BatchesWithRawResponse(client.batches)
        self.uploads = uploads.UploadsWithRawResponse(client.uploads)


class AsyncOpenAIWithRawResponse:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.completions = completions.AsyncCompletionsWithRawResponse(client.completions)
        self.chat = chat.AsyncChatWithRawResponse(client.chat)
        self.embeddings = embeddings.AsyncEmbeddingsWithRawResponse(client.embeddings)
        self.files = files.AsyncFilesWithRawResponse(client.files)
        self.images = images.AsyncImagesWithRawResponse(client.images)
        self.audio = audio.AsyncAudioWithRawResponse(client.audio)
        self.moderations = moderations.AsyncModerationsWithRawResponse(client.moderations)
        self.models = models.AsyncModelsWithRawResponse(client.models)
        self.fine_tuning = fine_tuning.AsyncFineTuningWithRawResponse(client.fine_tuning)
        self.beta = beta.AsyncBetaWithRawResponse(client.beta)
        self.batches = batches.AsyncBatchesWithRawResponse(client.batches)
        self.uploads = uploads.AsyncUploadsWithRawResponse(client.uploads)


class OpenAIWithStreamedResponse:
    def __init__(self, client: OpenAI) -> None:
        self.completions = completions.CompletionsWithStreamingResponse(client.completions)
        self.chat = chat.ChatWithStreamingResponse(client.chat)
        self.embeddings = embeddings.EmbeddingsWithStreamingResponse(client.embeddings)
        self.files = files.FilesWithStreamingResponse(client.files)
        self.images = images.ImagesWithStreamingResponse(client.images)
        self.audio = audio.AudioWithStreamingResponse(client.audio)
        self.moderations = moderations.ModerationsWithStreamingResponse(client.moderations)
        self.models = models.ModelsWithStreamingResponse(client.models)
        self.fine_tuning = fine_tuning.FineTuningWithStreamingResponse(client.fine_tuning)
        self.beta = beta.BetaWithStreamingResponse(client.beta)
        self.batches = batches.BatchesWithStreamingResponse(client.batches)
        self.uploads = uploads.UploadsWithStreamingResponse(client.uploads)


class AsyncOpenAIWithStreamedResponse:
    def __init__(self, client: AsyncOpenAI) -> None:
        self.completions = completions.AsyncCompletionsWithStreamingResponse(client.completions)
        self.chat = chat.AsyncChatWithStreamingResponse(client.chat)
        self.embeddings = embeddings.AsyncEmbeddingsWithStreamingResponse(client.embeddings)
        self.files = files.AsyncFilesWithStreamingResponse(client.files)
        self.images = images.AsyncImagesWithStreamingResponse(client.images)
        self.audio = audio.AsyncAudioWithStreamingResponse(client.audio)
        self.moderations = moderations.AsyncModerationsWithStreamingResponse(client.moderations)
        self.models = models.AsyncModelsWithStreamingResponse(client.models)
        self.fine_tuning = fine_tuning.AsyncFineTuningWithStreamingResponse(client.fine_tuning)
        self.beta = beta.AsyncBetaWithStreamingResponse(client.beta)
        self.batches = batches.AsyncBatchesWithStreamingResponse(client.batches)
        self.uploads = uploads.AsyncUploadsWithStreamingResponse(client.uploads)


Client = OpenAI

AsyncClient = AsyncOpenAI


================================================
File: /src/openai/_compat.py
================================================
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, Generic, TypeVar, Callable, cast, overload
from datetime import date, datetime
from typing_extensions import Self, Literal

import pydantic
from pydantic.fields import FieldInfo

from ._types import IncEx, StrBytesIntFloat

_T = TypeVar("_T")
_ModelT = TypeVar("_ModelT", bound=pydantic.BaseModel)

# --------------- Pydantic v2 compatibility ---------------

# Pyright incorrectly reports some of our functions as overriding a method when they don't
# pyright: reportIncompatibleMethodOverride=false

PYDANTIC_V2 = pydantic.VERSION.startswith("2.")

# v1 re-exports
if TYPE_CHECKING:

    def parse_date(value: date | StrBytesIntFloat) -> date:  # noqa: ARG001
        ...

    def parse_datetime(value: Union[datetime, StrBytesIntFloat]) -> datetime:  # noqa: ARG001
        ...

    def get_args(t: type[Any]) -> tuple[Any, ...]:  # noqa: ARG001
        ...

    def is_union(tp: type[Any] | None) -> bool:  # noqa: ARG001
        ...

    def get_origin(t: type[Any]) -> type[Any] | None:  # noqa: ARG001
        ...

    def is_literal_type(type_: type[Any]) -> bool:  # noqa: ARG001
        ...

    def is_typeddict(type_: type[Any]) -> bool:  # noqa: ARG001
        ...

else:
    if PYDANTIC_V2:
        from pydantic.v1.typing import (
            get_args as get_args,
            is_union as is_union,
            get_origin as get_origin,
            is_typeddict as is_typeddict,
            is_literal_type as is_literal_type,
        )
        from pydantic.v1.datetime_parse import parse_date as parse_date, parse_datetime as parse_datetime
    else:
        from pydantic.typing import (
            get_args as get_args,
            is_union as is_union,
            get_origin as get_origin,
            is_typeddict as is_typeddict,
            is_literal_type as is_literal_type,
        )
        from pydantic.datetime_parse import parse_date as parse_date, parse_datetime as parse_datetime


# refactored config
if TYPE_CHECKING:
    from pydantic import ConfigDict as ConfigDict
else:
    if PYDANTIC_V2:
        from pydantic import ConfigDict
    else:
        # TODO: provide an error message here?
        ConfigDict = None


# renamed methods / properties
def parse_obj(model: type[_ModelT], value: object) -> _ModelT:
    if PYDANTIC_V2:
        return model.model_validate(value)
    else:
        return cast(_ModelT, model.parse_obj(value))  # pyright: ignore[reportDeprecated, reportUnnecessaryCast]


def field_is_required(field: FieldInfo) -> bool:
    if PYDANTIC_V2:
        return field.is_required()
    return field.required  # type: ignore


def field_get_default(field: FieldInfo) -> Any:
    value = field.get_default()
    if PYDANTIC_V2:
        from pydantic_core import PydanticUndefined

        if value == PydanticUndefined:
            return None
        return value
    return value


def field_outer_type(field: FieldInfo) -> Any:
    if PYDANTIC_V2:
        return field.annotation
    return field.outer_type_  # type: ignore


def get_model_config(model: type[pydantic.BaseModel]) -> Any:
    if PYDANTIC_V2:
        return model.model_config
    return model.__config__  # type: ignore


def get_model_fields(model: type[pydantic.BaseModel]) -> dict[str, FieldInfo]:
    if PYDANTIC_V2:
        return model.model_fields
    return model.__fields__  # type: ignore


def model_copy(model: _ModelT, *, deep: bool = False) -> _ModelT:
    if PYDANTIC_V2:
        return model.model_copy(deep=deep)
    return model.copy(deep=deep)  # type: ignore


def model_json(model: pydantic.BaseModel, *, indent: int | None = None) -> str:
    if PYDANTIC_V2:
        return model.model_dump_json(indent=indent)
    return model.json(indent=indent)  # type: ignore


def model_dump(
    model: pydantic.BaseModel,
    *,
    exclude: IncEx | None = None,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    warnings: bool = True,
    mode: Literal["json", "python"] = "python",
) -> dict[str, Any]:
    if PYDANTIC_V2 or hasattr(model, "model_dump"):
        return model.model_dump(
            mode=mode,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            # warnings are not supported in Pydantic v1
            warnings=warnings if PYDANTIC_V2 else True,
        )
    return cast(
        "dict[str, Any]",
        model.dict(  # pyright: ignore[reportDeprecated, reportUnnecessaryCast]
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
        ),
    )


def model_parse(model: type[_ModelT], data: Any) -> _ModelT:
    if PYDANTIC_V2:
        return model.model_validate(data)
    return model.parse_obj(data)  # pyright: ignore[reportDeprecated]


def model_parse_json(model: type[_ModelT], data: str | bytes) -> _ModelT:
    if PYDANTIC_V2:
        return model.model_validate_json(data)
    return model.parse_raw(data)  # pyright: ignore[reportDeprecated]


def model_json_schema(model: type[_ModelT]) -> dict[str, Any]:
    if PYDANTIC_V2:
        return model.model_json_schema()
    return model.schema()  # pyright: ignore[reportDeprecated]


# generic models
if TYPE_CHECKING:

    class GenericModel(pydantic.BaseModel): ...

else:
    if PYDANTIC_V2:
        # there no longer needs to be a distinction in v2 but
        # we still have to create our own subclass to avoid
        # inconsistent MRO ordering errors
        class GenericModel(pydantic.BaseModel): ...

    else:
        import pydantic.generics

        class GenericModel(pydantic.generics.GenericModel, pydantic.BaseModel): ...


# cached properties
if TYPE_CHECKING:
    cached_property = property

    # we define a separate type (copied from typeshed)
    # that represents that `cached_property` is `set`able
    # at runtime, which differs from `@property`.
    #
    # this is a separate type as editors likely special case
    # `@property` and we don't want to cause issues just to have
    # more helpful internal types.

    class typed_cached_property(Generic[_T]):
        func: Callable[[Any], _T]
        attrname: str | None

        def __init__(self, func: Callable[[Any], _T]) -> None: ...

        @overload
        def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

        @overload
        def __get__(self, instance: object, owner: type[Any] | None = None) -> _T: ...

        def __get__(self, instance: object, owner: type[Any] | None = None) -> _T | Self:
            raise NotImplementedError()

        def __set_name__(self, owner: type[Any], name: str) -> None: ...

        # __set__ is not defined at runtime, but @cached_property is designed to be settable
        def __set__(self, instance: object, value: _T) -> None: ...
else:
    from functools import cached_property as cached_property

    typed_cached_property = cached_property


================================================
File: /src/openai/_constants.py
================================================
# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import httpx

RAW_RESPONSE_HEADER = "X-Stainless-Raw-Response"
OVERRIDE_CAST_TO_HEADER = "____stainless_override_cast_to"

# default timeout is 10 minutes
DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_MAX_RETRIES = 2
DEFAULT_CONNECTION_LIMITS = httpx.Limits(max_connections=1000, max_keepalive_connections=100)

INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0


================================================
File: /src/openai/_exceptions.py
================================================
# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, cast
from typing_extensions import Literal

import httpx

from ._utils import is_dict
from ._models import construct_type

if TYPE_CHECKING:
    from .types.chat import ChatCompletion

__all__ = [
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "LengthFinishReasonError",
    "ContentFilterFinishReasonError",
]


class OpenAIError(Exception):
    pass


class APIError(OpenAIError):
    message: str
    request: httpx.Request

    body: object | None
    """The API response body.

    If the API responded with a valid JSON structure then this property will be the
    decoded result.

    If it isn't a valid JSON structure then this will be the raw response.

    If there was no response associated with this error then it will be `None`.
    """

    code: Optional[str] = None
    param: Optional[str] = None
    type: Optional[str]

    def __init__(self, message: str, request: httpx.Request, *, body: object | None) -> None:
        super().__init__(message)
        self.request = request
        self.message = message
        self.body = body

        if is_dict(body):
            self.code = cast(Any, construct_type(type_=Optional[str], value=body.get("code")))
            self.param = cast(Any, construct_type(type_=Optional[str], value=body.get("param")))
            self.type = cast(Any, construct_type(type_=str, value=body.get("type")))
        else:
            self.code = None
            self.param = None
            self.type = None


class APIResponseValidationError(APIError):
    response: httpx.Response
    status_code: int

    def __init__(self, response: httpx.Response, body: object | None, *, message: str | None = None) -> None:
        super().__init__(message or "Data returned by API invalid for expected schema.", response.request, body=body)
        self.response = response
        self.status_code = response.status_code


class APIStatusError(APIError):
    """Raised when an API response has a status code of 4xx or 5xx."""

    response: httpx.Response
    status_code: int
    request_id: str | None

    def __init__(self, message: str, *, response: httpx.Response, body: object | None) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code
        self.request_id = response.headers.get("x-request-id")


class APIConnectionError(APIError):
    def __init__(self, *, message: str = "Connection error.", request: httpx.Request) -> None:
        super().__init__(message, request, body=None)


class APITimeoutError(APIConnectionError):
    def __init__(self, request: httpx.Request) -> None:
        super().__init__(message="Request timed out.", request=request)


class BadRequestError(APIStatusError):
    status_code: Literal[400] = 400  # pyright: ignore[reportIncompatibleVariableOverride]


class AuthenticationError(APIStatusError):
    status_code: Literal[401] = 401  # pyright: ignore[reportIncompatibleVariableOverride]


class PermissionDeniedError(APIStatusError):
    status_code: Literal[403] = 403  # pyright: ignore[reportIncompatibleVariableOverride]


class NotFoundError(APIStatusError):
    status_code: Literal[404] = 404  # pyright: ignore[reportIncompatibleVariableOverride]


class ConflictError(APIStatusError):
    status_code: Literal[409] = 409  # pyright: ignore[reportIncompatibleVariableOverride]


class UnprocessableEntityError(APIStatusError):
    status_code: Literal[422] = 422  # pyright: ignore[reportIncompatibleVariableOverride]


class RateLimitError(APIStatusError):
    status_code: Literal[429] = 429  # pyright: ignore[reportIncompatibleVariableOverride]


class InternalServerError(APIStatusError):
    pass


class LengthFinishReasonError(OpenAIError):
    completion: ChatCompletion
    """The completion that caused this error.

    Note: this will *not* be a complete `ChatCompletion` object when streaming as `usage`
          will not be included.
    """

    def __init__(self, *, completion: ChatCompletion) -> None:
        msg = "Could not parse response content as the length limit was reached"
        if completion.usage:
            msg += f" - {completion.usage}"

        super().__init__(msg)
        self.completion = completion


class ContentFilterFinishReasonError(OpenAIError):
    def __init__(self) -> None:
        super().__init__(
            f"Could not parse response content as the request was rejected by the content filter",
        )


================================================
File: /src/openai/_files.py
================================================
from __future__ import annotations

import io
import os
import pathlib
from typing import overload
from typing_extensions import TypeGuard

import anyio

from ._types import (
    FileTypes,
    FileContent,
    RequestFiles,
    HttpxFileTypes,
    Base64FileInput,
    HttpxFileContent,
    HttpxRequestFiles,
)
from ._utils import is_tuple_t, is_mapping_t, is_sequence_t


def is_base64_file_input(obj: object) -> TypeGuard[Base64FileInput]:
    return isinstance(obj, io.IOBase) or isinstance(obj, os.PathLike)


def is_file_content(obj: object) -> TypeGuard[FileContent]:
    return (
        isinstance(obj, bytes) or isinstance(obj, tuple) or isinstance(obj, io.IOBase) or isinstance(obj, os.PathLike)
    )


def assert_is_file_content(obj: object, *, key: str | None = None) -> None:
    if not is_file_content(obj):
        prefix = f"Expected entry at `{key}`" if key is not None else f"Expected file input `{obj!r}`"
        raise RuntimeError(
            f"{prefix} to be bytes, an io.IOBase instance, PathLike or a tuple but received {type(obj)} instead. See https://github.com/openai/openai-python/tree/main#file-uploads"
        ) from None


@overload
def to_httpx_files(files: None) -> None: ...


@overload
def to_httpx_files(files: RequestFiles) -> HttpxRequestFiles: ...


def to_httpx_files(files: RequestFiles | None) -> HttpxRequestFiles | None:
    if files is None:
        return None

    if is_mapping_t(files):
        files = {key: _transform_file(file) for key, file in files.items()}
    elif is_sequence_t(files):
        files = [(key, _transform_file(file)) for key, file in files]
    else:
        raise TypeError(f"Unexpected file type input {type(files)}, expected mapping or sequence")

    return files


def _transform_file(file: FileTypes) -> HttpxFileTypes:
    if is_file_content(file):
        if isinstance(file, os.PathLike):
            path = pathlib.Path(file)
            return (path.name, path.read_bytes())

        return file

    if is_tuple_t(file):
        return (file[0], _read_file_content(file[1]), *file[2:])

    raise TypeError(f"Expected file types input to be a FileContent type or to be a tuple")


def _read_file_content(file: FileContent) -> HttpxFileContent:
    if isinstance(file, os.PathLike):
        return pathlib.Path(file).read_bytes()
    return file


@overload
async def async_to_httpx_files(files: None) -> None: ...


@overload
async def async_to_httpx_files(files: RequestFiles) -> HttpxRequestFiles: ...


async def async_to_httpx_files(files: RequestFiles | None) -> HttpxRequestFiles | None:
    if files is None:
        return None

    if is_mapping_t(files):
        files = {key: await _async_transform_file(file) for key, file in files.items()}
    elif is_sequence_t(files):
        files = [(key, await _async_transform_file(file)) for key, file in files]
    else:
        raise TypeError("Unexpected file type input {type(files)}, expected mapping or sequence")

    return files


async def _async_transform_file(file: FileTypes) -> HttpxFileTypes:
    if is_file_content(file):
        if isinstance(file, os.PathLike):
            path = anyio.Path(file)
            return (path.name, await path.read_bytes())

        return file

    if is_tuple_t(file):
        return (file[0], await _async_read_file_content(file[1]), *file[2:])

    raise TypeError(f"Expected file types input to be a FileContent type or to be a tuple")


async def _async_read_file_content(file: FileContent) -> HttpxFileContent:
    if isinstance(file, os.PathLike):
        return await anyio.Path(file).read_bytes()

    return file


================================================
File: /src/openai/_legacy_response.py
================================================
from __future__ import annotations

import os
import inspect
import logging
import datetime
import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    Generic,
    TypeVar,
    Callable,
    Iterator,
    AsyncIterator,
    cast,
    overload,
)
from typing_extensions import Awaitable, ParamSpec, override, deprecated, get_origin

import anyio
import httpx
import pydantic

from ._types import NoneType
from ._utils import is_given, extract_type_arg, is_annotated_type, is_type_alias_type
from ._models import BaseModel, is_basemodel, add_request_id
from ._constants import RAW_RESPONSE_HEADER
from ._streaming import Stream, AsyncStream, is_stream_class_type, extract_stream_chunk_type
from ._exceptions import APIResponseValidationError

if TYPE_CHECKING:
    from ._models import FinalRequestOptions
    from ._base_client import BaseClient


P = ParamSpec("P")
R = TypeVar("R")
_T = TypeVar("_T")

log: logging.Logger = logging.getLogger(__name__)


class LegacyAPIResponse(Generic[R]):
    """This is a legacy class as it will be replaced by `APIResponse`
    and `AsyncAPIResponse` in the `_response.py` file in the next major
    release.

    For the sync client this will mostly be the same with the exception
    of `content` & `text` will be methods instead of properties. In the
    async client, all methods will be async.

    A migration script will be provided & the migration in general should
    be smooth.
    """

    _cast_to: type[R]
    _client: BaseClient[Any, Any]
    _parsed_by_type: dict[type[Any], Any]
    _stream: bool
    _stream_cls: type[Stream[Any]] | type[AsyncStream[Any]] | None
    _options: FinalRequestOptions

    http_response: httpx.Response

    retries_taken: int
    """The number of retries made. If no retries happened this will be `0`"""

    def __init__(
        self,
        *,
        raw: httpx.Response,
        cast_to: type[R],
        client: BaseClient[Any, Any],
        stream: bool,
        stream_cls: type[Stream[Any]] | type[AsyncStream[Any]] | None,
        options: FinalRequestOptions,
        retries_taken: int = 0,
    ) -> None:
        self._cast_to = cast_to
        self._client = client
        self._parsed_by_type = {}
        self._stream = stream
        self._stream_cls = stream_cls
        self._options = options
        self.http_response = raw
        self.retries_taken = retries_taken

    @property
    def request_id(self) -> str | None:
        return self.http_response.headers.get("x-request-id")  # type: ignore[no-any-return]

    @overload
    def parse(self, *, to: type[_T]) -> _T: ...

    @overload
    def parse(self) -> R: ...

    def parse(self, *, to: type[_T] | None = None) -> R | _T:
        """Returns the rich python representation of this response's data.

        NOTE: For the async client: this will become a coroutine in the next major version.

        For lower-level control, see `.read()`, `.json()`, `.iter_bytes()`.

        You can customise the type that the response is parsed into through
        the `to` argument, e.g.

        ```py
        from openai import BaseModel


        class MyModel(BaseModel):
            foo: str


        obj = response.parse(to=MyModel)
        print(obj.foo)
        ```

        We support parsing:
          - `BaseModel`
          - `dict`
          - `list`
          - `Union`
          - `str`
          - `int`
          - `float`
          - `httpx.Response`
        """
        cache_key = to if to is not None else self._cast_to
        cached = self._parsed_by_type.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        parsed = self._parse(to=to)
        if is_given(self._options.post_parser):
            parsed = self._options.post_parser(parsed)

        if isinstance(parsed, BaseModel):
            add_request_id(parsed, self.request_id)

        self._parsed_by_type[cache_key] = parsed
        return cast(R, parsed)

    @property
    def headers(self) -> httpx.Headers:
        return self.http_response.headers

    @property
    def http_request(self) -> httpx.Request:
        return self.http_response.request

    @property
    def status_code(self) -> int:
        return self.http_response.status_code

    @property
    def url(self) -> httpx.URL:
        return self.http_response.url

    @property
    def method(self) -> str:
        return self.http_request.method

    @property
    def content(self) -> bytes:
        """Return the binary response content.

        NOTE: this will be removed in favour of `.read()` in the
        next major version.
        """
        return self.http_response.content

    @property
    def text(self) -> str:
        """Return the decoded response content.

        NOTE: this will be turned into a method in the next major version.
        """
        return self.http_response.text

    @property
    def http_version(self) -> str:
        return self.http_response.http_version

    @property
    def is_closed(self) -> bool:
        return self.http_response.is_closed

    @property
    def elapsed(self) -> datetime.timedelta:
        """The time taken for the complete request/response cycle to complete."""
        return self.http_response.elapsed

    def _parse(self, *, to: type[_T] | None = None) -> R | _T:
        cast_to = to if to is not None else self._cast_to

        # unwrap `TypeAlias('Name', T)` -> `T`
        if is_type_alias_type(cast_to):
            cast_to = cast_to.__value__  # type: ignore[unreachable]

        # unwrap `Annotated[T, ...]` -> `T`
        if cast_to and is_annotated_type(cast_to):
            cast_to = extract_type_arg(cast_to, 0)

        if self._stream:
            if to:
                if not is_stream_class_type(to):
                    raise TypeError(f"Expected custom parse type to be a subclass of {Stream} or {AsyncStream}")

                return cast(
                    _T,
                    to(
                        cast_to=extract_stream_chunk_type(
                            to,
                            failure_message="Expected custom stream type to be passed with a type argument, e.g. Stream[ChunkType]",
                        ),
                        response=self.http_response,
                        client=cast(Any, self._client),
                    ),
                )

            if self._stream_cls:
                return cast(
                    R,
                    self._stream_cls(
                        cast_to=extract_stream_chunk_type(self._stream_cls),
                        response=self.http_response,
                        client=cast(Any, self._client),
                    ),
                )

            stream_cls = cast("type[Stream[Any]] | type[AsyncStream[Any]] | None", self._client._default_stream_cls)
            if stream_cls is None:
                raise MissingStreamClassError()

            return cast(
                R,
                stream_cls(
                    cast_to=cast_to,
                    response=self.http_response,
                    client=cast(Any, self._client),
                ),
            )

        if cast_to is NoneType:
            return cast(R, None)

        response = self.http_response
        if cast_to == str:
            return cast(R, response.text)

        if cast_to == int:
            return cast(R, int(response.text))

        if cast_to == float:
            return cast(R, float(response.text))

        if cast_to == bool:
            return cast(R, response.text.lower() == "true")

        origin = get_origin(cast_to) or cast_to

        if inspect.isclass(origin) and issubclass(origin, HttpxBinaryResponseContent):
            return cast(R, cast_to(response))  # type: ignore

        if origin == LegacyAPIResponse:
            raise RuntimeError("Unexpected state - cast_to is `APIResponse`")

        if inspect.isclass(origin) and issubclass(origin, httpx.Response):
            # Because of the invariance of our ResponseT TypeVar, users can subclass httpx.Response
            # and pass that class to our request functions. We cannot change the variance to be either
            # covariant or contravariant as that makes our usage of ResponseT illegal. We could construct
            # the response class ourselves but that is something that should be supported directly in httpx
            # as it would be easy to incorrectly construct the Response object due to the multitude of arguments.
            if cast_to != httpx.Response:
                raise ValueError(f"Subclasses of httpx.Response cannot be passed to `cast_to`")
            return cast(R, response)

        if inspect.isclass(origin) and not issubclass(origin, BaseModel) and issubclass(origin, pydantic.BaseModel):
            raise TypeError("Pydantic models must subclass our base model type, e.g. `from openai import BaseModel`")

        if (
            cast_to is not object
            and not origin is list
            and not origin is dict
            and not origin is Union
            and not issubclass(origin, BaseModel)
        ):
            raise RuntimeError(
                f"Unsupported type, expected {cast_to} to be a subclass of {BaseModel}, {dict}, {list}, {Union}, {NoneType}, {str} or {httpx.Response}."
            )

        # split is required to handle cases where additional information is included
        # in the response, e.g. application/json; charset=utf-8
        content_type, *_ = response.headers.get("content-type", "*").split(";")
        if content_type != "application/json":
            if is_basemodel(cast_to):
                try:
                    data = response.json()
                except Exception as exc:
                    log.debug("Could not read JSON from response data due to %s - %s", type(exc), exc)
                else:
                    return self._client._process_response_data(
                        data=data,
                        cast_to=cast_to,  # type: ignore
                        response=response,
                    )

            if self._client._strict_response_validation:
                raise APIResponseValidationError(
                    response=response,
                    message=f"Expected Content-Type response header to be `application/json` but received `{content_type}` instead.",
                    body=response.text,
                )

            # If the API responds with content that isn't JSON then we just return
            # the (decoded) text without performing any parsing so that you can still
            # handle the response however you need to.
            return response.text  # type: ignore

        data = response.json()

        return self._client._process_response_data(
            data=data,
            cast_to=cast_to,  # type: ignore
            response=response,
        )

    @override
    def __repr__(self) -> str:
        return f"<APIResponse [{self.status_code} {self.http_response.reason_phrase}] type={self._cast_to}>"


class MissingStreamClassError(TypeError):
    def __init__(self) -> None:
        super().__init__(
            "The `stream` argument was set to `True` but the `stream_cls` argument was not given. See `openai._streaming` for reference",
        )


def to_raw_response_wrapper(func: Callable[P, R]) -> Callable[P, LegacyAPIResponse[R]]:
    """Higher order function that takes one of our bound API methods and wraps it
    to support returning the raw `APIResponse` object directly.
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> LegacyAPIResponse[R]:
        extra_headers: dict[str, str] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "true"

        kwargs["extra_headers"] = extra_headers

        return cast(LegacyAPIResponse[R], func(*args, **kwargs))

    return wrapped


def async_to_raw_response_wrapper(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[LegacyAPIResponse[R]]]:
    """Higher order function that takes one of our bound API methods and wraps it
    to support returning the raw `APIResponse` object directly.
    """

    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> LegacyAPIResponse[R]:
        extra_headers: dict[str, str] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "true"

        kwargs["extra_headers"] = extra_headers

        return cast(LegacyAPIResponse[R], await func(*args, **kwargs))

    return wrapped


class HttpxBinaryResponseContent:
    response: httpx.Response

    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    @property
    def content(self) -> bytes:
        return self.response.content

    @property
    def text(self) -> str:
        return self.response.text

    @property
    def encoding(self) -> str | None:
        return self.response.encoding

    @property
    def charset_encoding(self) -> str | None:
        return self.response.charset_encoding

    def json(self, **kwargs: Any) -> Any:
        return self.response.json(**kwargs)

    def read(self) -> bytes:
        return self.response.read()

    def iter_bytes(self, chunk_size: int | None = None) -> Iterator[bytes]:
        return self.response.iter_bytes(chunk_size)

    def iter_text(self, chunk_size: int | None = None) -> Iterator[str]:
        return self.response.iter_text(chunk_size)

    def iter_lines(self) -> Iterator[str]:
        return self.response.iter_lines()

    def iter_raw(self, chunk_size: int | None = None) -> Iterator[bytes]:
        return self.response.iter_raw(chunk_size)

    def write_to_file(
        self,
        file: str | os.PathLike[str],
    ) -> None:
        """Write the output to the given file.

        Accepts a filename or any path-like object, e.g. pathlib.Path

        Note: if you want to stream the data to the file instead of writing
        all at once then you should use `.with_streaming_response` when making
        the API request, e.g. `client.with_streaming_response.foo().stream_to_file('my_filename.txt')`
        """
        with open(file, mode="wb") as f:
            for data in self.response.iter_bytes():
                f.write(data)

    @deprecated(
        "Due to a bug, this method doesn't actually stream the response content, `.with_streaming_response.method()` should be used instead"
    )
    def stream_to_file(
        self,
        file: str | os.PathLike[str],
        *,
        chunk_size: int | None = None,
    ) -> None:
        with open(file, mode="wb") as f:
            for data in self.response.iter_bytes(chunk_size):
                f.write(data)

    def close(self) -> None:
        return self.response.close()

    async def aread(self) -> bytes:
        return await self.response.aread()

    async def aiter_bytes(self, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        return self.response.aiter_bytes(chunk_size)

    async def aiter_text(self, chunk_size: int | None = None) -> AsyncIterator[str]:
        return self.response.aiter_text(chunk_size)

    async def aiter_lines(self) -> AsyncIterator[str]:
        return self.response.aiter_lines()

    async def aiter_raw(self, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        return self.response.aiter_raw(chunk_size)

    @deprecated(
        "Due to a bug, this method doesn't actually stream the response content, `.with_streaming_response.method()` should be used instead"
    )
    async def astream_to_file(
        self,
        file: str | os.PathLike[str],
        *,
        chunk_size: int | None = None,
    ) -> None:
        path = anyio.Path(file)
        async with await path.open(mode="wb") as f:
            async for data in self.response.aiter_bytes(chunk_size):
                await f.write(data)

    async def aclose(self) -> None:
        return await self.response.aclose()


================================================
File: /src/openai/_models.py
================================================
from __future__ import annotations

import os
import inspect
from typing import TYPE_CHECKING, Any, Type, Tuple, Union, Generic, TypeVar, Callable, Optional, cast
from datetime import date, datetime
from typing_extensions import (
    Unpack,
    Literal,
    ClassVar,
    Protocol,
    Required,
    Sequence,
    ParamSpec,
    TypedDict,
    TypeGuard,
    final,
    override,
    runtime_checkable,
)

import pydantic
import pydantic.generics
from pydantic.fields import FieldInfo

from ._types import (
    Body,
    IncEx,
    Query,
    ModelT,
    Headers,
    Timeout,
    NotGiven,
    AnyMapping,
    HttpxRequestFiles,
)
from ._utils import (
    PropertyInfo,
    is_list,
    is_given,
    json_safe,
    lru_cache,
    is_mapping,
    parse_date,
    coerce_boolean,
    parse_datetime,
    strip_not_given,
    extract_type_arg,
    is_annotated_type,
    is_type_alias_type,
    strip_annotated_type,
)
from ._compat import (
    PYDANTIC_V2,
    ConfigDict,
    GenericModel as BaseGenericModel,
    get_args,
    is_union,
    parse_obj,
    get_origin,
    is_literal_type,
    get_model_config,
    get_model_fields,
    field_get_default,
)
from ._constants import RAW_RESPONSE_HEADER

if TYPE_CHECKING:
    from pydantic_core.core_schema import ModelField, LiteralSchema, ModelFieldsSchema

__all__ = ["BaseModel", "GenericModel"]

_T = TypeVar("_T")
_BaseModelT = TypeVar("_BaseModelT", bound="BaseModel")

P = ParamSpec("P")

ReprArgs = Sequence[Tuple[Optional[str], Any]]


@runtime_checkable
class _ConfigProtocol(Protocol):
    allow_population_by_field_name: bool


class BaseModel(pydantic.BaseModel):
    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(
            extra="allow", defer_build=coerce_boolean(os.environ.get("DEFER_PYDANTIC_BUILD", "true"))
        )
    else:

        @property
        @override
        def model_fields_set(self) -> set[str]:
            # a forwards-compat shim for pydantic v2
            return self.__fields_set__  # type: ignore

        class Config(pydantic.BaseConfig):  # pyright: ignore[reportDeprecated]
            extra: Any = pydantic.Extra.allow  # type: ignore

        @override
        def __repr_args__(self) -> ReprArgs:
            # we don't want these attributes to be included when something like `rich.print` is used
            return [arg for arg in super().__repr_args__() if arg[0] not in {"_request_id", "__exclude_fields__"}]

    if TYPE_CHECKING:
        _request_id: Optional[str] = None
        """The ID of the request, returned via the X-Request-ID header. Useful for debugging requests and reporting issues to OpenAI.

        This will **only** be set for the top-level response object, it will not be defined for nested objects. For example:
        
        ```py
        completion = await client.chat.completions.create(...)
        completion._request_id  # req_id_xxx
        completion.usage._request_id  # raises `AttributeError`
        ```

        Note: unlike other properties that use an `_` prefix, this property
        *is* public. Unless documented otherwise, all other `_` prefix properties,
        methods and modules are *private*.
        """

    def to_dict(
        self,
        *,
        mode: Literal["json", "python"] = "python",
        use_api_names: bool = True,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        warnings: bool = True,
    ) -> dict[str, object]:
        """Recursively generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

        By default, fields that were not set by the API will not be included,
        and keys will match the API response, *not* the property names from the model.

        For example, if the API responds with `"fooBar": true` but we've defined a `foo_bar: bool` property,
        the output will use the `"fooBar"` key (unless `use_api_names=False` is passed).

        Args:
            mode:
                If mode is 'json', the dictionary will only contain JSON serializable types. e.g. `datetime` will be turned into a string, `"2024-3-22T18:11:19.117000Z"`.
                If mode is 'python', the dictionary may contain any Python objects. e.g. `datetime(2024, 3, 22)`

            use_api_names: Whether to use the key that the API responded with or the property name. Defaults to `True`.
            exclude_unset: Whether to exclude fields that have not been explicitly set.
            exclude_defaults: Whether to exclude fields that are set to their default value from the output.
            exclude_none: Whether to exclude fields that have a value of `None` from the output.
            warnings: Whether to log warnings when invalid fields are encountered. This is only supported in Pydantic v2.
        """
        return self.model_dump(
            mode=mode,
            by_alias=use_api_names,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            warnings=warnings,
        )

    def to_json(
        self,
        *,
        indent: int | None = 2,
        use_api_names: bool = True,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        warnings: bool = True,
    ) -> str:
        """Generates a JSON string representing this model as it would be received from or sent to the API (but with indentation).

        By default, fields that were not set by the API will not be included,
        and keys will match the API response, *not* the property names from the model.

        For example, if the API responds with `"fooBar": true` but we've defined a `foo_bar: bool` property,
        the output will use the `"fooBar"` key (unless `use_api_names=False` is passed).

        Args:
            indent: Indentation to use in the JSON output. If `None` is passed, the output will be compact. Defaults to `2`
            use_api_names: Whether to use the key that the API responded with or the property name. Defaults to `True`.
            exclude_unset: Whether to exclude fields that have not been explicitly set.
            exclude_defaults: Whether to exclude fields that have the default value.
            exclude_none: Whether to exclude fields that have a value of `None`.
            warnings: Whether to show any warnings that occurred during serialization. This is only supported in Pydantic v2.
        """
        return self.model_dump_json(
            indent=indent,
            by_alias=use_api_names,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            warnings=warnings,
        )

    @override
    def __str__(self) -> str:
        # mypy complains about an invalid self arg
        return f'{self.__repr_name__()}({self.__repr_str__(", ")})'  # type: ignore[misc]

    # Override the 'construct' method in a way that supports recursive parsing without validation.
    # Based on https://github.com/samuelcolvin/pydantic/issues/1168#issuecomment-817742836.
    @classmethod
    @override
    def construct(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls: Type[ModelT],
        _fields_set: set[str] | None = None,
        **values: object,
    ) -> ModelT:
        m = cls.__new__(cls)
        fields_values: dict[str, object] = {}

        config = get_model_config(cls)
        populate_by_name = (
            config.allow_population_by_field_name
            if isinstance(config, _ConfigProtocol)
            else config.get("populate_by_name")
        )

        if _fields_set is None:
            _fields_set = set()

        model_fields = get_model_fields(cls)
        for name, field in model_fields.items():
            key = field.alias
            if key is None or (key not in values and populate_by_name):
                key = name

            if key in values:
                fields_values[name] = _construct_field(value=values[key], field=field, key=key)
                _fields_set.add(name)
            else:
                fields_values[name] = field_get_default(field)

        _extra = {}
        for key, value in values.items():
            if key not in model_fields:
                if PYDANTIC_V2:
                    _extra[key] = value
                else:
                    _fields_set.add(key)
                    fields_values[key] = value

        object.__setattr__(m, "__dict__", fields_values)

        if PYDANTIC_V2:
            # these properties are copied from Pydantic's `model_construct()` method
            object.__setattr__(m, "__pydantic_private__", None)
            object.__setattr__(m, "__pydantic_extra__", _extra)
            object.__setattr__(m, "__pydantic_fields_set__", _fields_set)
        else:
            # init_private_attributes() does not exist in v2
            m._init_private_attributes()  # type: ignore

            # copied from Pydantic v1's `construct()` method
            object.__setattr__(m, "__fields_set__", _fields_set)

        return m

    if not TYPE_CHECKING:
        # type checkers incorrectly complain about this assignment
        # because the type signatures are technically different
        # although not in practice
        model_construct = construct

    if not PYDANTIC_V2:
        # we define aliases for some of the new pydantic v2 methods so
        # that we can just document these methods without having to specify
        # a specific pydantic version as some users may not know which
        # pydantic version they are currently using

        @override
        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal["none", "warn", "error"] = True,
            context: dict[str, Any] | None = None,
            serialize_as_any: bool = False,
        ) -> dict[str, Any]:
            """Usage docs: https://docs.pydantic.dev/2.4/concepts/serialization/#modelmodel_dump

            Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

            Args:
                mode: The mode in which `to_python` should run.
                    If mode is 'json', the dictionary will only contain JSON serializable types.
                    If mode is 'python', the dictionary may contain any Python objects.
                include: A list of fields to include in the output.
                exclude: A list of fields to exclude from the output.
                by_alias: Whether to use the field's alias in the dictionary key if defined.
                exclude_unset: Whether to exclude fields that are unset or None from the output.
                exclude_defaults: Whether to exclude fields that are set to their default value from the output.
                exclude_none: Whether to exclude fields that have a value of `None` from the output.
                round_trip: Whether to enable serialization and deserialization round-trip support.
                warnings: Whether to log warnings when invalid fields are encountered.

            Returns:
                A dictionary representation of the model.
            """
            if mode not in {"json", "python"}:
                raise ValueError("mode must be either 'json' or 'python'")
            if round_trip != False:
                raise ValueError("round_trip is only supported in Pydantic v2")
            if warnings != True:
                raise ValueError("warnings is only supported in Pydantic v2")
            if context is not None:
                raise ValueError("context is only supported in Pydantic v2")
            if serialize_as_any != False:
                raise ValueError("serialize_as_any is only supported in Pydantic v2")
            dumped = super().dict(  # pyright: ignore[reportDeprecated]
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )

            return cast(dict[str, Any], json_safe(dumped)) if mode == "json" else dumped

        @override
        def model_dump_json(
            self,
            *,
            indent: int | None = None,
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal["none", "warn", "error"] = True,
            context: dict[str, Any] | None = None,
            serialize_as_any: bool = False,
        ) -> str:
            """Usage docs: https://docs.pydantic.dev/2.4/concepts/serialization/#modelmodel_dump_json

            Generates a JSON representation of the model using Pydantic's `to_json` method.

            Args:
                indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
                include: Field(s) to include in the JSON output. Can take either a string or set of strings.
                exclude: Field(s) to exclude from the JSON output. Can take either a string or set of strings.
                by_alias: Whether to serialize using field aliases.
                exclude_unset: Whether to exclude fields that have not been explicitly set.
                exclude_defaults: Whether to exclude fields that have the default value.
                exclude_none: Whether to exclude fields that have a value of `None`.
                round_trip: Whether to use serialization/deserialization between JSON and class instance.
                warnings: Whether to show any warnings that occurred during serialization.

            Returns:
                A JSON string representation of the model.
            """
            if round_trip != False:
                raise ValueError("round_trip is only supported in Pydantic v2")
            if warnings != True:
                raise ValueError("warnings is only supported in Pydantic v2")
            if context is not None:
                raise ValueError("context is only supported in Pydantic v2")
            if serialize_as_any != False:
                raise ValueError("serialize_as_any is only supported in Pydantic v2")
            return super().json(  # type: ignore[reportDeprecated]
                indent=indent,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )


def _construct_field(value: object, field: FieldInfo, key: str) -> object:
    if value is None:
        return field_get_default(field)

    if PYDANTIC_V2:
        type_ = field.annotation
    else:
        type_ = cast(type, field.outer_type_)  # type: ignore

    if type_ is None:
        raise RuntimeError(f"Unexpected field type is None for {key}")

    return construct_type(value=value, type_=type_)


def is_basemodel(type_: type) -> bool:
    """Returns whether or not the given type is either a `BaseModel` or a union of `BaseModel`"""
    if is_union(type_):
        for variant in get_args(type_):
            if is_basemodel(variant):
                return True

        return False

    return is_basemodel_type(type_)


def is_basemodel_type(type_: type) -> TypeGuard[type[BaseModel] | type[GenericModel]]:
    origin = get_origin(type_) or type_
    if not inspect.isclass(origin):
        return False
    return issubclass(origin, BaseModel) or issubclass(origin, GenericModel)


def build(
    base_model_cls: Callable[P, _BaseModelT],
    *args: P.args,
    **kwargs: P.kwargs,
) -> _BaseModelT:
    """Construct a BaseModel class without validation.

    This is useful for cases where you need to instantiate a `BaseModel`
    from an API response as this provides type-safe params which isn't supported
    by helpers like `construct_type()`.

    ```py
    build(MyModel, my_field_a="foo", my_field_b=123)
    ```
    """
    if args:
        raise TypeError(
            "Received positional arguments which are not supported; Keyword arguments must be used instead",
        )

    return cast(_BaseModelT, construct_type(type_=base_model_cls, value=kwargs))


def construct_type_unchecked(*, value: object, type_: type[_T]) -> _T:
    """Loose coercion to the expected type with construction of nested values.

    Note: the returned value from this function is not guaranteed to match the
    given type.
    """
    return cast(_T, construct_type(value=value, type_=type_))


def construct_type(*, value: object, type_: object) -> object:
    """Loose coercion to the expected type with construction of nested values.

    If the given value does not match the expected type then it is returned as-is.
    """
    # we allow `object` as the input type because otherwise, passing things like
    # `Literal['value']` will be reported as a type error by type checkers
    type_ = cast("type[object]", type_)
    if is_type_alias_type(type_):
        type_ = type_.__value__  # type: ignore[unreachable]

    # unwrap `Annotated[T, ...]` -> `T`
    if is_annotated_type(type_):
        meta: tuple[Any, ...] = get_args(type_)[1:]
        type_ = extract_type_arg(type_, 0)
    else:
        meta = tuple()

    # we need to use the origin class for any types that are subscripted generics
    # e.g. Dict[str, object]
    origin = get_origin(type_) or type_
    args = get_args(type_)

    if is_union(origin):
        try:
            return validate_type(type_=cast("type[object]", type_), value=value)
        except Exception:
            pass

        # if the type is a discriminated union then we want to construct the right variant
        # in the union, even if the data doesn't match exactly, otherwise we'd break code
        # that relies on the constructed class types, e.g.
        #
        # class FooType:
        #   kind: Literal['foo']
        #   value: str
        #
        # class BarType:
        #   kind: Literal['bar']
        #   value: int
        #
        # without this block, if the data we get is something like `{'kind': 'bar', 'value': 'foo'}` then
        # we'd end up constructing `FooType` when it should be `BarType`.
        discriminator = _build_discriminated_union_meta(union=type_, meta_annotations=meta)
        if discriminator and is_mapping(value):
            variant_value = value.get(discriminator.field_alias_from or discriminator.field_name)
            if variant_value and isinstance(variant_value, str):
                variant_type = discriminator.mapping.get(variant_value)
                if variant_type:
                    return construct_type(type_=variant_type, value=value)

        # if the data is not valid, use the first variant that doesn't fail while deserializing
        for variant in args:
            try:
                return construct_type(value=value, type_=variant)
            except Exception:
                continue

        raise RuntimeError(f"Could not convert data into a valid instance of {type_}")

    if origin == dict:
        if not is_mapping(value):
            return value

        _, items_type = get_args(type_)  # Dict[_, items_type]
        return {key: construct_type(value=item, type_=items_type) for key, item in value.items()}

    if not is_literal_type(type_) and (issubclass(origin, BaseModel) or issubclass(origin, GenericModel)):
        if is_list(value):
            return [cast(Any, type_).construct(**entry) if is_mapping(entry) else entry for entry in value]

        if is_mapping(value):
            if issubclass(type_, BaseModel):
                return type_.construct(**value)  # type: ignore[arg-type]

            return cast(Any, type_).construct(**value)

    if origin == list:
        if not is_list(value):
            return value

        inner_type = args[0]  # List[inner_type]
        return [construct_type(value=entry, type_=inner_type) for entry in value]

    if origin == float:
        if isinstance(value, int):
            coerced = float(value)
            if coerced != value:
                return value
            return coerced

        return value

    if type_ == datetime:
        try:
            return parse_datetime(value)  # type: ignore
        except Exception:
            return value

    if type_ == date:
        try:
            return parse_date(value)  # type: ignore
        except Exception:
            return value

    return value


@runtime_checkable
class CachedDiscriminatorType(Protocol):
    __discriminator__: DiscriminatorDetails


class DiscriminatorDetails:
    field_name: str
    """The name of the discriminator field in the variant class, e.g.

    ```py
    class Foo(BaseModel):
        type: Literal['foo']
    ```

    Will result in field_name='type'
    """

    field_alias_from: str | None
    """The name of the discriminator field in the API response, e.g.

    ```py
    class Foo(BaseModel):
        type: Literal['foo'] = Field(alias='type_from_api')
    ```

    Will result in field_alias_from='type_from_api'
    """

    mapping: dict[str, type]
    """Mapping of discriminator value to variant type, e.g.

    {'foo': FooVariant, 'bar': BarVariant}
    """

    def __init__(
        self,
        *,
        mapping: dict[str, type],
        discriminator_field: str,
        discriminator_alias: str | None,
    ) -> None:
        self.mapping = mapping
        self.field_name = discriminator_field
        self.field_alias_from = discriminator_alias


def _build_discriminated_union_meta(*, union: type, meta_annotations: tuple[Any, ...]) -> DiscriminatorDetails | None:
    if isinstance(union, CachedDiscriminatorType):
        return union.__discriminator__

    discriminator_field_name: str | None = None

    for annotation in meta_annotations:
        if isinstance(annotation, PropertyInfo) and annotation.discriminator is not None:
            discriminator_field_name = annotation.discriminator
            break

    if not discriminator_field_name:
        return None

    mapping: dict[str, type] = {}
    discriminator_alias: str | None = None

    for variant in get_args(union):
        variant = strip_annotated_type(variant)
        if is_basemodel_type(variant):
            if PYDANTIC_V2:
                field = _extract_field_schema_pv2(variant, discriminator_field_name)
                if not field:
                    continue

                # Note: if one variant defines an alias then they all should
                discriminator_alias = field.get("serialization_alias")

                field_schema = field["schema"]

                if field_schema["type"] == "literal":
                    for entry in cast("LiteralSchema", field_schema)["expected"]:
                        if isinstance(entry, str):
                            mapping[entry] = variant
            else:
                field_info = cast("dict[str, FieldInfo]", variant.__fields__).get(discriminator_field_name)  # pyright: ignore[reportDeprecated, reportUnnecessaryCast]
                if not field_info:
                    continue

                # Note: if one variant defines an alias then they all should
                discriminator_alias = field_info.alias

                if field_info.annotation and is_literal_type(field_info.annotation):
                    for entry in get_args(field_info.annotation):
                        if isinstance(entry, str):
                            mapping[entry] = variant

    if not mapping:
        return None

    details = DiscriminatorDetails(
        mapping=mapping,
        discriminator_field=discriminator_field_name,
        discriminator_alias=discriminator_alias,
    )
    cast(CachedDiscriminatorType, union).__discriminator__ = details
    return details


def _extract_field_schema_pv2(model: type[BaseModel], field_name: str) -> ModelField | None:
    schema = model.__pydantic_core_schema__
    if schema["type"] != "model":
        return None

    fields_schema = schema["schema"]
    if fields_schema["type"] != "model-fields":
        return None

    fields_schema = cast("ModelFieldsSchema", fields_schema)

    field = fields_schema["fields"].get(field_name)
    if not field:
        return None

    return cast("ModelField", field)  # pyright: ignore[reportUnnecessaryCast]


def validate_type(*, type_: type[_T], value: object) -> _T:
    """Strict validation that the given value matches the expected type"""
    if inspect.isclass(type_) and issubclass(type_, pydantic.BaseModel):
        return cast(_T, parse_obj(type_, value))

    return cast(_T, _validate_non_model_type(type_=type_, value=value))


def set_pydantic_config(typ: Any, config: pydantic.ConfigDict) -> None:
    """Add a pydantic config for the given type.

    Note: this is a no-op on Pydantic v1.
    """
    setattr(typ, "__pydantic_config__", config)  # noqa: B010


def add_request_id(obj: BaseModel, request_id: str | None) -> None:
    obj._request_id = request_id

    # in Pydantic v1, using setattr like we do above causes the attribute
    # to be included when serializing the model which we don't want in this
    # case so we need to explicitly exclude it
    if not PYDANTIC_V2:
        try:
            exclude_fields = obj.__exclude_fields__  # type: ignore
        except AttributeError:
            cast(Any, obj).__exclude_fields__ = {"_request_id", "__exclude_fields__"}
        else:
            cast(Any, obj).__exclude_fields__ = {*(exclude_fields or {}), "_request_id", "__exclude_fields__"}


# our use of subclasssing here causes weirdness for type checkers,
# so we just pretend that we don't subclass
if TYPE_CHECKING:
    GenericModel = BaseModel
else:

    class GenericModel(BaseGenericModel, BaseModel):
        pass


if PYDANTIC_V2:
    from pydantic import TypeAdapter as _TypeAdapter

    _CachedTypeAdapter = cast("TypeAdapter[object]", lru_cache(maxsize=None)(_TypeAdapter))

    if TYPE_CHECKING:
        from pydantic import TypeAdapter
    else:
        TypeAdapter = _CachedTypeAdapter

    def _validate_non_model_type(*, type_: type[_T], value: object) -> _T:
        return TypeAdapter(type_).validate_python(value)

elif not TYPE_CHECKING:  # TODO: condition is weird

    class RootModel(GenericModel, Generic[_T]):
        """Used as a placeholder to easily convert runtime types to a Pydantic format
        to provide validation.

        For example:
        ```py
        validated = RootModel[int](__root__="5").__root__
        # validated: 5
        ```
        """

        __root__: _T

    def _validate_non_model_type(*, type_: type[_T], value: object) -> _T:
        model = _create_pydantic_model(type_).validate(value)
        return cast(_T, model.__root__)

    def _create_pydantic_model(type_: _T) -> Type[RootModel[_T]]:
        return RootModel[type_]  # type: ignore


class FinalRequestOptionsInput(TypedDict, total=False):
    method: Required[str]
    url: Required[str]
    params: Query
    headers: Headers
    max_retries: int
    timeout: float | Timeout | None
    files: HttpxRequestFiles | None
    idempotency_key: str
    json_data: Body
    extra_json: AnyMapping


@final
class FinalRequestOptions(pydantic.BaseModel):
    method: str
    url: str
    params: Query = {}
    headers: Union[Headers, NotGiven] = NotGiven()
    max_retries: Union[int, NotGiven] = NotGiven()
    timeout: Union[float, Timeout, None, NotGiven] = NotGiven()
    files: Union[HttpxRequestFiles, None] = None
    idempotency_key: Union[str, None] = None
    post_parser: Union[Callable[[Any], Any], NotGiven] = NotGiven()

    # It should be noted that we cannot use `json` here as that would override
    # a BaseModel method in an incompatible fashion.
    json_data: Union[Body, None] = None
    extra_json: Union[AnyMapping, None] = None

    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)
    else:

        class Config(pydantic.BaseConfig):  # pyright: ignore[reportDeprecated]
            arbitrary_types_allowed: bool = True

    def get_max_retries(self, max_retries: int) -> int:
        if isinstance(self.max_retries, NotGiven):
            return max_retries
        return self.max_retries

    def _strip_raw_response_header(self) -> None:
        if not is_given(self.headers):
            return

        if self.headers.get(RAW_RESPONSE_HEADER):
            self.headers = {**self.headers}
            self.headers.pop(RAW_RESPONSE_HEADER)

    # override the `construct` method so that we can run custom transformations.
    # this is necessary as we don't want to do any actual runtime type checking
    # (which means we can't use validators) but we do want to ensure that `NotGiven`
    # values are not present
    #
    # type ignore required because we're adding explicit types to `**values`
    @classmethod
    def construct(  # type: ignore
        cls,
        _fields_set: set[str] | None = None,
        **values: Unpack[FinalRequestOptionsInput],
    ) -> FinalRequestOptions:
        kwargs: dict[str, Any] = {
            # we unconditionally call `strip_not_given` on any value
            # as it will just ignore any non-mapping types
            key: strip_not_given(value)
            for key, value in values.items()
        }
        if PYDANTIC_V2:
            return super().model_construct(_fields_set, **kwargs)
        return cast(FinalRequestOptions, super().construct(_fields_set, **kwargs))  # pyright: ignore[reportDeprecated]

    if not TYPE_CHECKING:
        # type checkers incorrectly complain about this assignment
        model_construct = construct


================================================
File: /src/openai/_module_client.py
================================================
# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import override

from . import resources, _load_client
from ._utils import LazyProxy


class ChatProxy(LazyProxy[resources.Chat]):
    @override
    def __load__(self) -> resources.Chat:
        return _load_client().chat


class BetaProxy(LazyProxy[resources.Beta]):
    @override
    def __load__(self) -> resources.Beta:
        return _load_client().beta


class FilesProxy(LazyProxy[resources.Files]):
    @override
    def __load__(self) -> resources.Files:
        return _load_client().files


class AudioProxy(LazyProxy[resources.Audio]):
    @override
    def __load__(self) -> resources.Audio:
        return _load_client().audio


class ImagesProxy(LazyProxy[resources.Images]):
    @override
    def __load__(self) -> resources.Images:
        return _load_client().images


class ModelsProxy(LazyProxy[resources.Models]):
    @override
    def __load__(self) -> resources.Models:
        return _load_client().models


class BatchesProxy(LazyProxy[resources.Batches]):
    @override
    def __load__(self) -> resources.Batches:
        return _load_client().batches


class EmbeddingsProxy(LazyProxy[resources.Embeddings]):
    @override
    def __load__(self) -> resources.Embeddings:
        return _load_client().embeddings


class CompletionsProxy(LazyProxy[resources.Completions]):
    @override
    def __load__(self) -> resources.Completions:
        return _load_client().completions


class ModerationsProxy(LazyProxy[resources.Moderations]):
    @override
    def __load__(self) -> resources.Moderations:
        return _load_client().moderations


class FineTuningProxy(LazyProxy[resources.FineTuning]):
    @override
    def __load__(self) -> resources.FineTuning:
        return _load_client().fine_tuning


chat: resources.Chat = ChatProxy().__as_proxied__()
beta: resources.Beta = BetaProxy().__as_proxied__()
files: resources.Files = FilesProxy().__as_proxied__()
audio: resources.Audio = AudioProxy().__as_proxied__()
images: resources.Images = ImagesProxy().__as_proxied__()
models: resources.Models = ModelsProxy().__as_proxied__()
batches: resources.Batches = BatchesProxy().__as_proxied__()
embeddings: resources.Embeddings = EmbeddingsProxy().__as_proxied__()
completions: resources.Completions = CompletionsProxy().__as_proxied__()
moderations: resources.Moderations = ModerationsProxy().__as_proxied__()
fine_tuning: resources.FineTuning = FineTuningProxy().__as_proxied__()


================================================
File: /src/openai/_qs.py
================================================
from __future__ import annotations

from typing import Any, List, Tuple, Union, Mapping, TypeVar
from urllib.parse import parse_qs, urlencode
from typing_extensions import Literal, get_args

from ._types import NOT_GIVEN, NotGiven, NotGivenOr
from ._utils import flatten

_T = TypeVar("_T")


ArrayFormat = Literal["comma", "repeat", "indices", "brackets"]
NestedFormat = Literal["dots", "brackets"]

PrimitiveData = Union[str, int, float, bool, None]
# this should be Data = Union[PrimitiveData, "List[Data]", "Tuple[Data]", "Mapping[str, Data]"]
# https://github.com/microsoft/pyright/issues/3555
Data = Union[PrimitiveData, List[Any], Tuple[Any], "Mapping[str, Any]"]
Params = Mapping[str, Data]


class Querystring:
    array_format: ArrayFormat
    nested_format: NestedFormat

    def __init__(
        self,
        *,
        array_format: ArrayFormat = "repeat",
        nested_format: NestedFormat = "brackets",
    ) -> None:
        self.array_format = array_format
        self.nested_format = nested_format

    def parse(self, query: str) -> Mapping[str, object]:
        # Note: custom format syntax is not supported yet
        return parse_qs(query)

    def stringify(
        self,
        params: Params,
        *,
        array_format: NotGivenOr[ArrayFormat] = NOT_GIVEN,
        nested_format: NotGivenOr[NestedFormat] = NOT_GIVEN,
    ) -> str:
        return urlencode(
            self.stringify_items(
                params,
                array_format=array_format,
                nested_format=nested_format,
            )
        )

    def stringify_items(
        self,
        params: Params,
        *,
        array_format: NotGivenOr[ArrayFormat] = NOT_GIVEN,
        nested_format: NotGivenOr[NestedFormat] = NOT_GIVEN,
    ) -> list[tuple[str, str]]:
        opts = Options(
            qs=self,
            array_format=array_format,
            nested_format=nested_format,
        )
        return flatten([self._stringify_item(key, value, opts) for key, value in params.items()])

    def _stringify_item(
        self,
        key: str,
        value: Data,
        opts: Options,
    ) -> list[tuple[str, str]]:
        if isinstance(value, Mapping):
            items: list[tuple[str, str]] = []
            nested_format = opts.nested_format
            for subkey, subvalue in value.items():
                items.extend(
                    self._stringify_item(
                        # TODO: error if unknown format
                        f"{key}.{subkey}" if nested_format == "dots" else f"{key}[{subkey}]",
                        subvalue,
                        opts,
                    )
                )
            return items

        if isinstance(value, (list, tuple)):
            array_format = opts.array_format
            if array_format == "comma":
                return [
                    (
                        key,
                        ",".join(self._primitive_value_to_str(item) for item in value if item is not None),
                    ),
                ]
            elif array_format == "repeat":
                items = []
                for item in value:
                    items.extend(self._stringify_item(key, item, opts))
                return items
            elif array_format == "indices":
                raise NotImplementedError("The array indices format is not supported yet")
            elif array_format == "brackets":
                items = []
                key = key + "[]"
                for item in value:
                    items.extend(self._stringify_item(key, item, opts))
                return items
            else:
                raise NotImplementedError(
                    f"Unknown array_format value: {array_format}, choose from {', '.join(get_args(ArrayFormat))}"
                )

        serialised = self._primitive_value_to_str(value)
        if not serialised:
            return []
        return [(key, serialised)]

    def _primitive_value_to_str(self, value: PrimitiveData) -> str:
        # copied from httpx
        if value is True:
            return "true"
        elif value is False:
            return "false"
        elif value is None:
            return ""
        return str(value)


_qs = Querystring()
parse = _qs.parse
stringify = _qs.stringify
stringify_items = _qs.stringify_items


class Options:
    array_format: ArrayFormat
    nested_format: NestedFormat

    def __init__(
        self,
        qs: Querystring = _qs,
        *,
        array_format: NotGivenOr[ArrayFormat] = NOT_GIVEN,
        nested_format: NotGivenOr[NestedFormat] = NOT_GIVEN,
    ) -> None:
        self.array_format = qs.array_format if isinstance(array_format, NotGiven) else array_format
        self.nested_format = qs.nested_format if isinstance(nested_format, NotGiven) else nested_format


================================================
File: /src/openai/_resource.py
================================================
# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import anyio

if TYPE_CHECKING:
    from ._client import OpenAI, AsyncOpenAI


class SyncAPIResource:
    _client: OpenAI

    def __init__(self, client: OpenAI) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete
        self._get_api_list = client.get_api_list

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class AsyncAPIResource:
    _client: AsyncOpenAI

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client
        self._get = client.get
        self._post = client.post
        self._patch = client.patch
        self._put = client.put
        self._delete = client.delete
        self._get_api_list = client.get_api_list

    async def _sleep(self, seconds: float) -> None:
        await anyio.sleep(seconds)


================================================
File: /src/openai/_response.py
================================================
from __future__ import annotations

import os
import inspect
import logging
import datetime
import functools
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    Generic,
    TypeVar,
    Callable,
    Iterator,
    AsyncIterator,
    cast,
    overload,
)
from typing_extensions import Awaitable, ParamSpec, override, get_origin

import anyio
import httpx
import pydantic

from ._types import NoneType
from ._utils import is_given, extract_type_arg, is_annotated_type, is_type_alias_type, extract_type_var_from_base
from ._models import BaseModel, is_basemodel, add_request_id
from ._constants import RAW_RESPONSE_HEADER, OVERRIDE_CAST_TO_HEADER
from ._streaming import Stream, AsyncStream, is_stream_class_type, extract_stream_chunk_type
from ._exceptions import OpenAIError, APIResponseValidationError

if TYPE_CHECKING:
    from ._models import FinalRequestOptions
    from ._base_client import BaseClient


P = ParamSpec("P")
R = TypeVar("R")
_T = TypeVar("_T")
_APIResponseT = TypeVar("_APIResponseT", bound="APIResponse[Any]")
_AsyncAPIResponseT = TypeVar("_AsyncAPIResponseT", bound="AsyncAPIResponse[Any]")

log: logging.Logger = logging.getLogger(__name__)


class BaseAPIResponse(Generic[R]):
    _cast_to: type[R]
    _client: BaseClient[Any, Any]
    _parsed_by_type: dict[type[Any], Any]
    _is_sse_stream: bool
    _stream_cls: type[Stream[Any]] | type[AsyncStream[Any]] | None
    _options: FinalRequestOptions

    http_response: httpx.Response

    retries_taken: int
    """The number of retries made. If no retries happened this will be `0`"""

    def __init__(
        self,
        *,
        raw: httpx.Response,
        cast_to: type[R],
        client: BaseClient[Any, Any],
        stream: bool,
        stream_cls: type[Stream[Any]] | type[AsyncStream[Any]] | None,
        options: FinalRequestOptions,
        retries_taken: int = 0,
    ) -> None:
        self._cast_to = cast_to
        self._client = client
        self._parsed_by_type = {}
        self._is_sse_stream = stream
        self._stream_cls = stream_cls
        self._options = options
        self.http_response = raw
        self.retries_taken = retries_taken

    @property
    def headers(self) -> httpx.Headers:
        return self.http_response.headers

    @property
    def http_request(self) -> httpx.Request:
        """Returns the httpx Request instance associated with the current response."""
        return self.http_response.request

    @property
    def status_code(self) -> int:
        return self.http_response.status_code

    @property
    def url(self) -> httpx.URL:
        """Returns the URL for which the request was made."""
        return self.http_response.url

    @property
    def method(self) -> str:
        return self.http_request.method

    @property
    def http_version(self) -> str:
        return self.http_response.http_version

    @property
    def elapsed(self) -> datetime.timedelta:
        """The time taken for the complete request/response cycle to complete."""
        return self.http_response.elapsed

    @property
    def is_closed(self) -> bool:
        """Whether or not the response body has been closed.

        If this is False then there is response data that has not been read yet.
        You must either fully consume the response body or call `.close()`
        before discarding the response to prevent resource leaks.
        """
        return self.http_response.is_closed

    @override
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} [{self.status_code} {self.http_response.reason_phrase}] type={self._cast_to}>"
        )

    def _parse(self, *, to: type[_T] | None = None) -> R | _T:
        cast_to = to if to is not None else self._cast_to

        # unwrap `TypeAlias('Name', T)` -> `T`
        if is_type_alias_type(cast_to):
            cast_to = cast_to.__value__  # type: ignore[unreachable]

        # unwrap `Annotated[T, ...]` -> `T`
        if cast_to and is_annotated_type(cast_to):
            cast_to = extract_type_arg(cast_to, 0)

        if self._is_sse_stream:
            if to:
                if not is_stream_class_type(to):
                    raise TypeError(f"Expected custom parse type to be a subclass of {Stream} or {AsyncStream}")

                return cast(
                    _T,
                    to(
                        cast_to=extract_stream_chunk_type(
                            to,
                            failure_message="Expected custom stream type to be passed with a type argument, e.g. Stream[ChunkType]",
                        ),
                        response=self.http_response,
                        client=cast(Any, self._client),
                    ),
                )

            if self._stream_cls:
                return cast(
                    R,
                    self._stream_cls(
                        cast_to=extract_stream_chunk_type(self._stream_cls),
                        response=self.http_response,
                        client=cast(Any, self._client),
                    ),
                )

            stream_cls = cast("type[Stream[Any]] | type[AsyncStream[Any]] | None", self._client._default_stream_cls)
            if stream_cls is None:
                raise MissingStreamClassError()

            return cast(
                R,
                stream_cls(
                    cast_to=cast_to,
                    response=self.http_response,
                    client=cast(Any, self._client),
                ),
            )

        if cast_to is NoneType:
            return cast(R, None)

        response = self.http_response
        if cast_to == str:
            return cast(R, response.text)

        if cast_to == bytes:
            return cast(R, response.content)

        if cast_to == int:
            return cast(R, int(response.text))

        if cast_to == float:
            return cast(R, float(response.text))

        if cast_to == bool:
            return cast(R, response.text.lower() == "true")

        origin = get_origin(cast_to) or cast_to

        # handle the legacy binary response case
        if inspect.isclass(cast_to) and cast_to.__name__ == "HttpxBinaryResponseContent":
            return cast(R, cast_to(response))  # type: ignore

        if origin == APIResponse:
            raise RuntimeError("Unexpected state - cast_to is `APIResponse`")

        if inspect.isclass(origin) and issubclass(origin, httpx.Response):
            # Because of the invariance of our ResponseT TypeVar, users can subclass httpx.Response
            # and pass that class to our request functions. We cannot change the variance to be either
            # covariant or contravariant as that makes our usage of ResponseT illegal. We could construct
            # the response class ourselves but that is something that should be supported directly in httpx
            # as it would be easy to incorrectly construct the Response object due to the multitude of arguments.
            if cast_to != httpx.Response:
                raise ValueError(f"Subclasses of httpx.Response cannot be passed to `cast_to`")
            return cast(R, response)

        if inspect.isclass(origin) and not issubclass(origin, BaseModel) and issubclass(origin, pydantic.BaseModel):
            raise TypeError("Pydantic models must subclass our base model type, e.g. `from openai import BaseModel`")

        if (
            cast_to is not object
            and not origin is list
            and not origin is dict
            and not origin is Union
            and not issubclass(origin, BaseModel)
        ):
            raise RuntimeError(
                f"Unsupported type, expected {cast_to} to be a subclass of {BaseModel}, {dict}, {list}, {Union}, {NoneType}, {str} or {httpx.Response}."
            )

        # split is required to handle cases where additional information is included
        # in the response, e.g. application/json; charset=utf-8
        content_type, *_ = response.headers.get("content-type", "*").split(";")
        if content_type != "application/json":
            if is_basemodel(cast_to):
                try:
                    data = response.json()
                except Exception as exc:
                    log.debug("Could not read JSON from response data due to %s - %s", type(exc), exc)
                else:
                    return self._client._process_response_data(
                        data=data,
                        cast_to=cast_to,  # type: ignore
                        response=response,
                    )

            if self._client._strict_response_validation:
                raise APIResponseValidationError(
                    response=response,
                    message=f"Expected Content-Type response header to be `application/json` but received `{content_type}` instead.",
                    body=response.text,
                )

            # If the API responds with content that isn't JSON then we just return
            # the (decoded) text without performing any parsing so that you can still
            # handle the response however you need to.
            return response.text  # type: ignore

        data = response.json()

        return self._client._process_response_data(
            data=data,
            cast_to=cast_to,  # type: ignore
            response=response,
        )


class APIResponse(BaseAPIResponse[R]):
    @property
    def request_id(self) -> str | None:
        return self.http_response.headers.get("x-request-id")  # type: ignore[no-any-return]

    @overload
    def parse(self, *, to: type[_T]) -> _T: ...

    @overload
    def parse(self) -> R: ...

    def parse(self, *, to: type[_T] | None = None) -> R | _T:
        """Returns the rich python representation of this response's data.

        For lower-level control, see `.read()`, `.json()`, `.iter_bytes()`.

        You can customise the type that the response is parsed into through
        the `to` argument, e.g.

        ```py
        from openai import BaseModel


        class MyModel(BaseModel):
            foo: str


        obj = response.parse(to=MyModel)
        print(obj.foo)
        ```

        We support parsing:
          - `BaseModel`
          - `dict`
          - `list`
          - `Union`
          - `str`
          - `int`
          - `float`
          - `httpx.Response`
        """
        cache_key = to if to is not None else self._cast_to
        cached = self._parsed_by_type.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        if not self._is_sse_stream:
            self.read()

        parsed = self._parse(to=to)
        if is_given(self._options.post_parser):
            parsed = self._options.post_parser(parsed)

        if isinstance(parsed, BaseModel):
            add_request_id(parsed, self.request_id)

        self._parsed_by_type[cache_key] = parsed
        return cast(R, parsed)

    def read(self) -> bytes:
        """Read and return the binary response content."""
        try:
            return self.http_response.read()
        except httpx.StreamConsumed as exc:
            # The default error raised by httpx isn't very
            # helpful in our case so we re-raise it with
            # a different error message.
            raise StreamAlreadyConsumed() from exc

    def text(self) -> str:
        """Read and decode the response content into a string."""
        self.read()
        return self.http_response.text

    def json(self) -> object:
        """Read and decode the JSON response content."""
        self.read()
        return self.http_response.json()

    def close(self) -> None:
        """Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        self.http_response.close()

    def iter_bytes(self, chunk_size: int | None = None) -> Iterator[bytes]:
        """
        A byte-iterator over the decoded response content.

        This automatically handles gzip, deflate and brotli encoded responses.
        """
        for chunk in self.http_response.iter_bytes(chunk_size):
            yield chunk

    def iter_text(self, chunk_size: int | None = None) -> Iterator[str]:
        """A str-iterator over the decoded response content
        that handles both gzip, deflate, etc but also detects the content's
        string encoding.
        """
        for chunk in self.http_response.iter_text(chunk_size):
            yield chunk

    def iter_lines(self) -> Iterator[str]:
        """Like `iter_text()` but will only yield chunks for each line"""
        for chunk in self.http_response.iter_lines():
            yield chunk


class AsyncAPIResponse(BaseAPIResponse[R]):
    @property
    def request_id(self) -> str | None:
        return self.http_response.headers.get("x-request-id")  # type: ignore[no-any-return]

    @overload
    async def parse(self, *, to: type[_T]) -> _T: ...

    @overload
    async def parse(self) -> R: ...

    async def parse(self, *, to: type[_T] | None = None) -> R | _T:
        """Returns the rich python representation of this response's data.

        For lower-level control, see `.read()`, `.json()`, `.iter_bytes()`.

        You can customise the type that the response is parsed into through
        the `to` argument, e.g.

        ```py
        from openai import BaseModel


        class MyModel(BaseModel):
            foo: str


        obj = response.parse(to=MyModel)
        print(obj.foo)
        ```

        We support parsing:
          - `BaseModel`
          - `dict`
          - `list`
          - `Union`
          - `str`
          - `httpx.Response`
        """
        cache_key = to if to is not None else self._cast_to
        cached = self._parsed_by_type.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[no-any-return]

        if not self._is_sse_stream:
            await self.read()

        parsed = self._parse(to=to)
        if is_given(self._options.post_parser):
            parsed = self._options.post_parser(parsed)

        if isinstance(parsed, BaseModel):
            add_request_id(parsed, self.request_id)

        self._parsed_by_type[cache_key] = parsed
        return cast(R, parsed)

    async def read(self) -> bytes:
        """Read and return the binary response content."""
        try:
            return await self.http_response.aread()
        except httpx.StreamConsumed as exc:
            # the default error raised by httpx isn't very
            # helpful in our case so we re-raise it with
            # a different error message
            raise StreamAlreadyConsumed() from exc

    async def text(self) -> str:
        """Read and decode the response content into a string."""
        await self.read()
        return self.http_response.text

    async def json(self) -> object:
        """Read and decode the JSON response content."""
        await self.read()
        return self.http_response.json()

    async def close(self) -> None:
        """Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        await self.http_response.aclose()

    async def iter_bytes(self, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        """
        A byte-iterator over the decoded response content.

        This automatically handles gzip, deflate and brotli encoded responses.
        """
        async for chunk in self.http_response.aiter_bytes(chunk_size):
            yield chunk

    async def iter_text(self, chunk_size: int | None = None) -> AsyncIterator[str]:
        """A str-iterator over the decoded response content
        that handles both gzip, deflate, etc but also detects the content's
        string encoding.
        """
        async for chunk in self.http_response.aiter_text(chunk_size):
            yield chunk

    async def iter_lines(self) -> AsyncIterator[str]:
        """Like `iter_text()` but will only yield chunks for each line"""
        async for chunk in self.http_response.aiter_lines():
            yield chunk


class BinaryAPIResponse(APIResponse[bytes]):
    """Subclass of APIResponse providing helpers for dealing with binary data.

    Note: If you want to stream the response data instead of eagerly reading it
    all at once then you should use `.with_streaming_response` when making
    the API request, e.g. `.with_streaming_response.get_binary_response()`
    """

    def write_to_file(
        self,
        file: str | os.PathLike[str],
    ) -> None:
        """Write the output to the given file.

        Accepts a filename or any path-like object, e.g. pathlib.Path

        Note: if you want to stream the data to the file instead of writing
        all at once then you should use `.with_streaming_response` when making
        the API request, e.g. `.with_streaming_response.get_binary_response()`
        """
        with open(file, mode="wb") as f:
            for data in self.iter_bytes():
                f.write(data)


class AsyncBinaryAPIResponse(AsyncAPIResponse[bytes]):
    """Subclass of APIResponse providing helpers for dealing with binary data.

    Note: If you want to stream the response data instead of eagerly reading it
    all at once then you should use `.with_streaming_response` when making
    the API request, e.g. `.with_streaming_response.get_binary_response()`
    """

    async def write_to_file(
        self,
        file: str | os.PathLike[str],
    ) -> None:
        """Write the output to the given file.

        Accepts a filename or any path-like object, e.g. pathlib.Path

        Note: if you want to stream the data to the file instead of writing
        all at once then you should use `.with_streaming_response` when making
        the API request, e.g. `.with_streaming_response.get_binary_response()`
        """
        path = anyio.Path(file)
        async with await path.open(mode="wb") as f:
            async for data in self.iter_bytes():
                await f.write(data)


class StreamedBinaryAPIResponse(APIResponse[bytes]):
    def stream_to_file(
        self,
        file: str | os.PathLike[str],
        *,
        chunk_size: int | None = None,
    ) -> None:
        """Streams the output to the given file.

        Accepts a filename or any path-like object, e.g. pathlib.Path
        """
        with open(file, mode="wb") as f:
            for data in self.iter_bytes(chunk_size):
                f.write(data)


class AsyncStreamedBinaryAPIResponse(AsyncAPIResponse[bytes]):
    async def stream_to_file(
        self,
        file: str | os.PathLike[str],
        *,
        chunk_size: int | None = None,
    ) -> None:
        """Streams the output to the given file.

        Accepts a filename or any path-like object, e.g. pathlib.Path
        """
        path = anyio.Path(file)
        async with await path.open(mode="wb") as f:
            async for data in self.iter_bytes(chunk_size):
                await f.write(data)


class MissingStreamClassError(TypeError):
    def __init__(self) -> None:
        super().__init__(
            "The `stream` argument was set to `True` but the `stream_cls` argument was not given. See `openai._streaming` for reference",
        )


class StreamAlreadyConsumed(OpenAIError):
    """
    Attempted to read or stream content, but the content has already
    been streamed.

    This can happen if you use a method like `.iter_lines()` and then attempt
    to read th entire response body afterwards, e.g.

    ```py
    response = await client.post(...)
    async for line in response.iter_lines():
        ...  # do something with `line`

    content = await response.read()
    # ^ error
    ```

    If you want this behaviour you'll need to either manually accumulate the response
    content or call `await response.read()` before iterating over the stream.
    """

    def __init__(self) -> None:
        message = (
            "Attempted to read or stream some content, but the content has "
            "already been streamed. "
            "This could be due to attempting to stream the response "
            "content more than once."
            "\n\n"
            "You can fix this by manually accumulating the response content while streaming "
            "or by calling `.read()` before starting to stream."
        )
        super().__init__(message)


class ResponseContextManager(Generic[_APIResponseT]):
    """Context manager for ensuring that a request is not made
    until it is entered and that the response will always be closed
    when the context manager exits
    """

    def __init__(self, request_func: Callable[[], _APIResponseT]) -> None:
        self._request_func = request_func
        self.__response: _APIResponseT | None = None

    def __enter__(self) -> _APIResponseT:
        self.__response = self._request_func()
        return self.__response

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.__response is not None:
            self.__response.close()


class AsyncResponseContextManager(Generic[_AsyncAPIResponseT]):
    """Context manager for ensuring that a request is not made
    until it is entered and that the response will always be closed
    when the context manager exits
    """

    def __init__(self, api_request: Awaitable[_AsyncAPIResponseT]) -> None:
        self._api_request = api_request
        self.__response: _AsyncAPIResponseT | None = None

    async def __aenter__(self) -> _AsyncAPIResponseT:
        self.__response = await self._api_request
        return self.__response

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.__response is not None:
            await self.__response.close()


def to_streamed_response_wrapper(func: Callable[P, R]) -> Callable[P, ResponseContextManager[APIResponse[R]]]:
    """Higher order function that takes one of our bound API methods and wraps it
    to support streaming and returning the raw `APIResponse` object directly.
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> ResponseContextManager[APIResponse[R]]:
        extra_headers: dict[str, str] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "stream"

        kwargs["extra_headers"] = extra_headers

        make_request = functools.partial(func, *args, **kwargs)

        return ResponseContextManager(cast(Callable[[], APIResponse[R]], make_request))

    return wrapped


def async_to_streamed_response_wrapper(
    func: Callable[P, Awaitable[R]],
) -> Callable[P, AsyncResponseContextManager[AsyncAPIResponse[R]]]:
    """Higher order function that takes one of our bound API methods and wraps it
    to support streaming and returning the raw `APIResponse` object directly.
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> AsyncResponseContextManager[AsyncAPIResponse[R]]:
        extra_headers: dict[str, str] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "stream"

        kwargs["extra_headers"] = extra_headers

        make_request = func(*args, **kwargs)

        return AsyncResponseContextManager(cast(Awaitable[AsyncAPIResponse[R]], make_request))

    return wrapped


def to_custom_streamed_response_wrapper(
    func: Callable[P, object],
    response_cls: type[_APIResponseT],
) -> Callable[P, ResponseContextManager[_APIResponseT]]:
    """Higher order function that takes one of our bound API methods and an `APIResponse` class
    and wraps the method to support streaming and returning the given response class directly.

    Note: the given `response_cls` *must* be concrete, e.g. `class BinaryAPIResponse(APIResponse[bytes])`
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> ResponseContextManager[_APIResponseT]:
        extra_headers: dict[str, Any] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "stream"
        extra_headers[OVERRIDE_CAST_TO_HEADER] = response_cls

        kwargs["extra_headers"] = extra_headers

        make_request = functools.partial(func, *args, **kwargs)

        return ResponseContextManager(cast(Callable[[], _APIResponseT], make_request))

    return wrapped


def async_to_custom_streamed_response_wrapper(
    func: Callable[P, Awaitable[object]],
    response_cls: type[_AsyncAPIResponseT],
) -> Callable[P, AsyncResponseContextManager[_AsyncAPIResponseT]]:
    """Higher order function that takes one of our bound API methods and an `APIResponse` class
    and wraps the method to support streaming and returning the given response class directly.

    Note: the given `response_cls` *must* be concrete, e.g. `class BinaryAPIResponse(APIResponse[bytes])`
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> AsyncResponseContextManager[_AsyncAPIResponseT]:
        extra_headers: dict[str, Any] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "stream"
        extra_headers[OVERRIDE_CAST_TO_HEADER] = response_cls

        kwargs["extra_headers"] = extra_headers

        make_request = func(*args, **kwargs)

        return AsyncResponseContextManager(cast(Awaitable[_AsyncAPIResponseT], make_request))

    return wrapped


def to_raw_response_wrapper(func: Callable[P, R]) -> Callable[P, APIResponse[R]]:
    """Higher order function that takes one of our bound API methods and wraps it
    to support returning the raw `APIResponse` object directly.
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> APIResponse[R]:
        extra_headers: dict[str, str] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "raw"

        kwargs["extra_headers"] = extra_headers

        return cast(APIResponse[R], func(*args, **kwargs))

    return wrapped


def async_to_raw_response_wrapper(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[AsyncAPIResponse[R]]]:
    """Higher order function that takes one of our bound API methods and wraps it
    to support returning the raw `APIResponse` object directly.
    """

    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> AsyncAPIResponse[R]:
        extra_headers: dict[str, str] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "raw"

        kwargs["extra_headers"] = extra_headers

        return cast(AsyncAPIResponse[R], await func(*args, **kwargs))

    return wrapped


def to_custom_raw_response_wrapper(
    func: Callable[P, object],
    response_cls: type[_APIResponseT],
) -> Callable[P, _APIResponseT]:
    """Higher order function that takes one of our bound API methods and an `APIResponse` class
    and wraps the method to support returning the given response class directly.

    Note: the given `response_cls` *must* be concrete, e.g. `class BinaryAPIResponse(APIResponse[bytes])`
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> _APIResponseT:
        extra_headers: dict[str, Any] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "raw"
        extra_headers[OVERRIDE_CAST_TO_HEADER] = response_cls

        kwargs["extra_headers"] = extra_headers

        return cast(_APIResponseT, func(*args, **kwargs))

    return wrapped


def async_to_custom_raw_response_wrapper(
    func: Callable[P, Awaitable[object]],
    response_cls: type[_AsyncAPIResponseT],
) -> Callable[P, Awaitable[_AsyncAPIResponseT]]:
    """Higher order function that takes one of our bound API methods and an `APIResponse` class
    and wraps the method to support returning the given response class directly.

    Note: the given `response_cls` *must* be concrete, e.g. `class BinaryAPIResponse(APIResponse[bytes])`
    """

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Awaitable[_AsyncAPIResponseT]:
        extra_headers: dict[str, Any] = {**(cast(Any, kwargs.get("extra_headers")) or {})}
        extra_headers[RAW_RESPONSE_HEADER] = "raw"
        extra_headers[OVERRIDE_CAST_TO_HEADER] = response_cls

        kwargs["extra_headers"] = extra_headers

        return cast(Awaitable[_AsyncAPIResponseT], func(*args, **kwargs))

    return wrapped


def extract_response_type(typ: type[BaseAPIResponse[Any]]) -> type:
    """Given a type like `APIResponse[T]`, returns the generic type variable `T`.

    This also handles the case where a concrete subclass is given, e.g.
    ```py
    class MyResponse(APIResponse[bytes]):
        ...

    extract_response_type(MyResponse) -> bytes
    ```
    """
    return extract_type_var_from_base(
        typ,
        generic_bases=cast("tuple[type, ...]", (BaseAPIResponse, APIResponse, AsyncAPIResponse)),
        index=0,
    )


================================================
File: /src/openai/_streaming.py
================================================
# Note: initially copied from https://github.com/florimondmanca/httpx-sse/blob/master/src/httpx_sse/_decoders.py
from __future__ import annotations

import json
import inspect
from types import TracebackType
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Iterator, AsyncIterator, cast
from typing_extensions import Self, Protocol, TypeGuard, override, get_origin, runtime_checkable

import httpx

from ._utils import is_mapping, extract_type_var_from_base
from ._exceptions import APIError

if TYPE_CHECKING:
    from ._client import OpenAI, AsyncOpenAI


_T = TypeVar("_T")


class Stream(Generic[_T]):
    """Provides the core interface to iterate over a synchronous stream response."""

    response: httpx.Response

    _decoder: SSEBytesDecoder

    def __init__(
        self,
        *,
        cast_to: type[_T],
        response: httpx.Response,
        client: OpenAI,
    ) -> None:
        self.response = response
        self._cast_to = cast_to
        self._client = client
        self._decoder = client._make_sse_decoder()
        self._iterator = self.__stream__()

    def __next__(self) -> _T:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[_T]:
        for item in self._iterator:
            yield item

    def _iter_events(self) -> Iterator[ServerSentEvent]:
        yield from self._decoder.iter_bytes(self.response.iter_bytes())

    def __stream__(self) -> Iterator[_T]:
        cast_to = cast(Any, self._cast_to)
        response = self.response
        process_data = self._client._process_response_data
        iterator = self._iter_events()

        for sse in iterator:
            if sse.data.startswith("[DONE]"):
                break

            if sse.event is None:
                data = sse.json()
                if is_mapping(data) and data.get("error"):
                    message = None
                    error = data.get("error")
                    if is_mapping(error):
                        message = error.get("message")
                    if not message or not isinstance(message, str):
                        message = "An error occurred during streaming"

                    raise APIError(
                        message=message,
                        request=self.response.request,
                        body=data["error"],
                    )

                yield process_data(data=data, cast_to=cast_to, response=response)

            else:
                data = sse.json()

                if sse.event == "error" and is_mapping(data) and data.get("error"):
                    message = None
                    error = data.get("error")
                    if is_mapping(error):
                        message = error.get("message")
                    if not message or not isinstance(message, str):
                        message = "An error occurred during streaming"

                    raise APIError(
                        message=message,
                        request=self.response.request,
                        body=data["error"],
                    )

                yield process_data(data={"data": data, "event": sse.event}, cast_to=cast_to, response=response)

        # Ensure the entire stream is consumed
        for _sse in iterator:
            ...

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        self.response.close()


class AsyncStream(Generic[_T]):
    """Provides the core interface to iterate over an asynchronous stream response."""

    response: httpx.Response

    _decoder: SSEDecoder | SSEBytesDecoder

    def __init__(
        self,
        *,
        cast_to: type[_T],
        response: httpx.Response,
        client: AsyncOpenAI,
    ) -> None:
        self.response = response
        self._cast_to = cast_to
        self._client = client
        self._decoder = client._make_sse_decoder()
        self._iterator = self.__stream__()

    async def __anext__(self) -> _T:
        return await self._iterator.__anext__()

    async def __aiter__(self) -> AsyncIterator[_T]:
        async for item in self._iterator:
            yield item

    async def _iter_events(self) -> AsyncIterator[ServerSentEvent]:
        async for sse in self._decoder.aiter_bytes(self.response.aiter_bytes()):
            yield sse

    async def __stream__(self) -> AsyncIterator[_T]:
        cast_to = cast(Any, self._cast_to)
        response = self.response
        process_data = self._client._process_response_data
        iterator = self._iter_events()

        async for sse in iterator:
            if sse.data.startswith("[DONE]"):
                break

            if sse.event is None:
                data = sse.json()
                if is_mapping(data) and data.get("error"):
                    message = None
                    error = data.get("error")
                    if is_mapping(error):
                        message = error.get("message")
                    if not message or not isinstance(message, str):
                        message = "An error occurred during streaming"

                    raise APIError(
                        message=message,
                        request=self.response.request,
                        body=data["error"],
                    )

                yield process_data(data=data, cast_to=cast_to, response=response)

            else:
                data = sse.json()

                if sse.event == "error" and is_mapping(data) and data.get("error"):
                    message = None
                    error = data.get("error")
                    if is_mapping(error):
                        message = error.get("message")
                    if not message or not isinstance(message, str):
                        message = "An error occurred during streaming"

                    raise APIError(
                        message=message,
                        request=self.response.request,
                        body=data["error"],
                    )

                yield process_data(data={"data": data, "event": sse.event}, cast_to=cast_to, response=response)

        # Ensure the entire stream is consumed
        async for _sse in iterator:
            ...

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        await self.response.aclose()


class ServerSentEvent:
    def __init__(
        self,
        *,
        event: str | None = None,
        data: str | None = None,
        id: str | None = None,
        retry: int | None = None,
    ) -> None:
        if data is None:
            data = ""

        self._id = id
        self._data = data
        self._event = event or None
        self._retry = retry

    @property
    def event(self) -> str | None:
        return self._event

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def retry(self) -> int | None:
        return self._retry

    @property
    def data(self) -> str:
        return self._data

    def json(self) -> Any:
        return json.loads(self.data)

    @override
    def __repr__(self) -> str:
        return f"ServerSentEvent(event={self.event}, data={self.data}, id={self.id}, retry={self.retry})"


class SSEDecoder:
    _data: list[str]
    _event: str | None
    _retry: int | None
    _last_event_id: str | None

    def __init__(self) -> None:
        self._event = None
        self._data = []
        self._last_event_id = None
        self._retry = None

    def iter_bytes(self, iterator: Iterator[bytes]) -> Iterator[ServerSentEvent]:
        """Given an iterator that yields raw binary data, iterate over it & yield every event encountered"""
        for chunk in self._iter_chunks(iterator):
            # Split before decoding so splitlines() only uses \r and \n
            for raw_line in chunk.splitlines():
                line = raw_line.decode("utf-8")
                sse = self.decode(line)
                if sse:
                    yield sse

    def _iter_chunks(self, iterator: Iterator[bytes]) -> Iterator[bytes]:
        """Given an iterator that yields raw binary data, iterate over it and yield individual SSE chunks"""
        data = b""
        for chunk in iterator:
            for line in chunk.splitlines(keepends=True):
                data += line
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield data
                    data = b""
        if data:
            yield data

    async def aiter_bytes(self, iterator: AsyncIterator[bytes]) -> AsyncIterator[ServerSentEvent]:
        """Given an iterator that yields raw binary data, iterate over it & yield every event encountered"""
        async for chunk in self._aiter_chunks(iterator):
            # Split before decoding so splitlines() only uses \r and \n
            for raw_line in chunk.splitlines():
                line = raw_line.decode("utf-8")
                sse = self.decode(line)
                if sse:
                    yield sse

    async def _aiter_chunks(self, iterator: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
        """Given an iterator that yields raw binary data, iterate over it and yield individual SSE chunks"""
        data = b""
        async for chunk in iterator:
            for line in chunk.splitlines(keepends=True):
                data += line
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield data
                    data = b""
        if data:
            yield data

    def decode(self, line: str) -> ServerSentEvent | None:
        # See: https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation  # noqa: E501

        if not line:
            if not self._event and not self._data and not self._last_event_id and self._retry is None:
                return None

            sse = ServerSentEvent(
                event=self._event,
                data="\n".join(self._data),
                id=self._last_event_id,
                retry=self._retry,
            )

            # NOTE: as per the SSE spec, do not reset last_event_id.
            self._event = None
            self._data = []
            self._retry = None

            return sse

        if line.startswith(":"):
            return None

        fieldname, _, value = line.partition(":")

        if value.startswith(" "):
            value = value[1:]

        if fieldname == "event":
            self._event = value
        elif fieldname == "data":
            self._data.append(value)
        elif fieldname == "id":
            if "\0" in value:
                pass
            else:
                self._last_event_id = value
        elif fieldname == "retry":
            try:
                self._retry = int(value)
            except (TypeError, ValueError):
                pass
        else:
            pass  # Field is ignored.

        return None


@runtime_checkable
class SSEBytesDecoder(Protocol):
    def iter_bytes(self, iterator: Iterator[bytes]) -> Iterator[ServerSentEvent]:
        """Given an iterator that yields raw binary data, iterate over it & yield every event encountered"""
        ...

    def aiter_bytes(self, iterator: AsyncIterator[bytes]) -> AsyncIterator[ServerSentEvent]:
        """Given an async iterator that yields raw binary data, iterate over it & yield every event encountered"""
        ...


def is_stream_class_type(typ: type) -> TypeGuard[type[Stream[object]] | type[AsyncStream[object]]]:
    """TypeGuard for determining whether or not the given type is a subclass of `Stream` / `AsyncStream`"""
    origin = get_origin(typ) or typ
    return inspect.isclass(origin) and issubclass(origin, (Stream, AsyncStream))


def extract_stream_chunk_type(
    stream_cls: type,
    *,
    failure_message: str | None = None,
) -> type:
    """Given a type like `Stream[T]`, returns the generic type variable `T`.

    This also handles the case where a concrete subclass is given, e.g.
    ```py
    class MyStream(Stream[bytes]):
        ...

    extract_stream_chunk_type(MyStream) -> bytes
    ```
    """
    from ._base_client import Stream, AsyncStream

    return extract_type_var_from_base(
        stream_cls,
        index=0,
        generic_bases=cast("tuple[type, ...]", (Stream, AsyncStream)),
        failure_message=failure_message,
    )


================================================
File: /src/openai/_types.py
================================================
from __future__ import annotations

from os import PathLike
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    Tuple,
    Union,
    Mapping,
    TypeVar,
    Callable,
    Optional,
    Sequence,
)
from typing_extensions import Set, Literal, Protocol, TypeAlias, TypedDict, override, runtime_checkable

import httpx
import pydantic
from httpx import URL, Proxy, Timeout, Response, BaseTransport, AsyncBaseTransport

if TYPE_CHECKING:
    from ._models import BaseModel
    from ._response import APIResponse, AsyncAPIResponse
    from ._legacy_response import HttpxBinaryResponseContent

Transport = BaseTransport
AsyncTransport = AsyncBaseTransport
Query = Mapping[str, object]
Body = object
AnyMapping = Mapping[str, object]
ModelT = TypeVar("ModelT", bound=pydantic.BaseModel)
_T = TypeVar("_T")


# Approximates httpx internal ProxiesTypes and RequestFiles types
# while adding support for `PathLike` instances
ProxiesDict = Dict["str | URL", Union[None, str, URL, Proxy]]
ProxiesTypes = Union[str, Proxy, ProxiesDict]
if TYPE_CHECKING:
    Base64FileInput = Union[IO[bytes], PathLike[str]]
    FileContent = Union[IO[bytes], bytes, PathLike[str]]
else:
    Base64FileInput = Union[IO[bytes], PathLike]
    FileContent = Union[IO[bytes], bytes, PathLike]  # PathLike is not subscriptable in Python 3.8.
FileTypes = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    Tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    Tuple[Optional[str], FileContent, Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    Tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]
RequestFiles = Union[Mapping[str, FileTypes], Sequence[Tuple[str, FileTypes]]]

# duplicate of the above but without our custom file support
HttpxFileC