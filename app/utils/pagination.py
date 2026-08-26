def get_pagination_offset(page: int, size: int) -> int:
    return (page - 1) * size
