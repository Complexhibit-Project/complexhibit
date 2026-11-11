class SparqlError(Exception):
    """Base exception for SPARQL errors."""

    pass


class SparqlQueryError(SparqlError):
    """Exception raised for errors in the SPARQL query execution."""

    pass


class ResourceNotFoundError(Exception):
    """Exception raised when a requested resource is not found."""

    pass
