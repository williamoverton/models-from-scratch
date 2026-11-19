from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        total = rng.randint(80, 500)
        yield {"last_page": str(rng.randint(0, total)), "total": str(total)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(last_page, total):
    return str(int(total) - int(last_page))


SCHEMA = Schema(
    id="education_reading_progress",
    tool_names=('calculate_pages_remaining', 'compute_reading_remaining', 'compute_pages_remaining', 'count_unread_pages', 'calculate_unread_pages', 'get_reading_remaining', 'subtract_pages_read', 'remaining_book_pages', 'find_unread_page_count', 'calculate_book_pages_remaining'),
    descriptions=('Subtract the last page read from the total page count.', 'Calculate the number of unread pages.', 'Compute total pages minus the last page read.', 'Count unread pages by subtracting the last page read from the total.', 'Calculate unread pages from total pages and last page read.', 'Get reading remaining as total minus last page read.', 'Return the difference between total pages and the last page read.', 'Return book pages remaining after the last page read.', 'Find the unread page count using total and last page read.', 'Calculate remaining book pages as total minus last page read.'),
    parameters=(Parameter(names=("last_page", "last_page_read")), Parameter(names=("total", "total_pages"))),
    tasks=(Task(id="remaining", prompts=("A book has {total} pages. The student has read through page {last_page}; page 0 means none read. How many pages remain?", "The book is {total} pages long and the student finished page {last_page}. Page 0 means nothing has been read. How many pages are unread?", "How many pages are left in a {total}-page book after reading through page {last_page}? Treat page 0 as none read.", "A reader has reached page {last_page} of {total}; page 0 indicates no pages read. Find the remaining pages.", "Subtract the last page read, {last_page}, from the book's {total} pages; page 0 means none read. How many remain?", "Of a book's {total} pages, the student read through page {last_page}, or none if it is 0. Count the pages left.", "Reading progress: last page {last_page}, total pages {total}. Page 0 represents no reading. What remains?", "The student completed page {last_page} in a {total}-page book; 0 means no pages completed. How many pages still need reading?", "Given {total} total pages and {last_page} as the last page read (0 means none), calculate unread pages.", "For a book with {total} pages, find the pages after page {last_page}; if {last_page} is 0, none were read.", "A student is at the end of page {last_page} in a {total}-page book. If the page is 0, nothing was read. How many pages are left?"), answers=("There are {result} pages remaining.",), cases=cases),),
)
