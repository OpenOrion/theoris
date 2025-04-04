class Citation:
    def __init__(self, title: str) -> None:
        self.title = title

    @property
    def bibliography_mla(self) -> str:
        pass


class Website:
    def __init__(self, title: str, base_url: str) -> None:
        self.title = title
        self.base_url = base_url

    def citation(self, page_name: str, sub_url: str = None):
        return WebsiteCitation(self, page_name, sub_url)


class Book:
    def __init__(self, title: str, authors: list[str], publication_year: int = None, edition: int = None, volume: int = None) -> None:
        self.title = title
        self.authors = authors
        self.publication_year = publication_year
        self.edition = edition
        self.volume = volume

    def citation(self, page_number: int = None):
        return BookCitation(self, page_number)


class BookCitation(Citation):
    def __init__(self, book: Book, page_number: int = None) -> None:
        super().__init__(book.title)
        self.page_number = page_number

class WebsiteCitation(Citation):
    def __init__(self, website: Website, page_name: str, sub_url: str) -> None:
        self.url = website.base_url + sub_url
        super().__init__(page_name)