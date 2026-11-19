from ...schema_types import Decision, Parameter, Schema, Task


OWNERS = {'auth.py': 'Identity', 'billing.py': 'Payments', 'search.py': 'Discovery', 'catalog.py': 'Merchandising', 'profile.py': 'Accounts', 'deploy.py': 'Platform'}


def cases(rng, count):
    for _ in range(count):
        files = rng.sample(tuple(OWNERS), 3)
        yield {'files': ', '.join(files), 'file': rng.choice(files)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={'file': case['file']})


def resolve(file):
    return f'{file}: {OWNERS[file]}'


SCHEMA = Schema(
    id='development_file_code_owner',
    tool_names=('get_code_owner', 'lookup_code_owner', 'find_code_owner', 'get_file_owner', 'lookup_file_owner', 'find_file_owner', 'retrieve_code_owner', 'read_owner_registry', 'identify_file_owner', 'query_code_owner'),
    descriptions=('Look up the file owner in the sample registry.', 'Find a file owner in the sample registry.', 'Find a file’s owner in the sample registry.', 'Get the registered owner of a sample file.', 'Look up the supplied file in the sample owner registry.', 'Find the registered code owner for a file.', 'Retrieve a file owner from the sample registry.', 'Read the sample registry owner for a file.', 'Identify the registered owner of the supplied file.', 'Query the sample code-owner registry for a file.'),
    parameters=(Parameter(names=('file', 'file_path')),),
    tasks=(Task(id='owner', prompts=('Files: {files}. Look up the code owner of {file} in the sample registry.', 'From {files}, look up the registered code owner for {file}.', 'In the sample owner registry, who owns {file}? The files are {files}.', 'Find the registered code owner for {file}; the file list is {files}.', 'Look up {file} in the sample code-owner registry. Files: {files}.', 'Which owner does the sample registry assign to {file}? Available files: {files}.', 'For {file}, retrieve the code owner from the sample registry; files: {files}.', 'The files are {files}. Please find the registered owner of {file}.', 'Using the sample registry, identify the code owner of {file} among {files}.', 'Check the sample owner registry for {file}; the file list is {files}.', 'Who is the registered code owner of {file} in the sample registry? Files: {files}.', 'From the file list {files}, get the sample registry owner for {file}.'), answers=('Owner: {result}.', 'The registry lists {result}.'), cases=cases),),
)
