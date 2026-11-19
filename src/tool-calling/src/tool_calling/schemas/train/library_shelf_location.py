from ...schema_types import Decision, Parameter, Schema, Task


SHELVES = {"C-101": ("Central", "A-12"), "C-102": ("North", "B-04"), "C-103": ("East", "C-21"), "C-104": ("Central", "D-07"), "C-105": ("North", "E-15"), "C-106": ("East", "F-09")}


def cases(rng, count):
    for _ in range(count):
        yield {"catalog_id": rng.choice(tuple(SHELVES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(catalog_id):
    branch, shelf = SHELVES[catalog_id]
    return f"{branch} branch, shelf {shelf}"


SCHEMA = Schema(
    id="library_shelf_location",
    tool_names=("lookup_library_shelf", "find_book_shelf", "get_catalog_shelf_location", "lookup_book_branch_and_shelf", "find_catalog_location", "retrieve_library_shelf", "locate_catalog_record", "get_book_shelf_location", "lookup_catalog_branch", "find_library_book_location"),
    descriptions=("Look up the branch and shelf for a catalog ID.", "Find a catalog record's branch and shelf location.", "Retrieve the library branch and shelf associated with a catalog identifier.", "Locate a book's recorded branch and shelf by catalog ID.", "Get the shelf and branch for the specified library catalog record.", "Find where a cataloged item is shelved.", "Look up the recorded location of a library item using its catalog ID.", "Return the branch and shelf corresponding to a book ID.", "Retrieve the branch and shelf for a selected catalog entry.", "Find a library item's recorded shelving location by identifier."),
    parameters=(Parameter(names=("catalog_id", "book_id")),),
    tasks=(Task(id="lookup", prompts=("Which branch and shelf hold catalog ID {catalog_id}?", "Find the branch and shelf location for library catalog ID {catalog_id}.", "Where is library catalog item {catalog_id} shelved? Give its branch and shelf.", "Look up both the branch and shelf for the catalog entry {catalog_id}.", "At which library branch and shelf can catalog ID {catalog_id} be found?", "For catalog ID {catalog_id}, report the recorded library branch and shelf.", "Retrieve the library shelving location of {catalog_id}, including branch and shelf.", "What branch and shelf are listed for the library item with catalog ID {catalog_id}?", "Locate catalog record {catalog_id} by its library branch and shelf.", "I need the branch name and shelf associated with library catalog ID {catalog_id}.", "Consult the library catalog for {catalog_id} and give its branch and shelf location.", "Identify the shelf and branch where the library records place {catalog_id}."), answers=("The location is {result}.", "The catalog lists {result}."), cases=cases),),
)
