def retrieve_origin(cell_positions):
    for p in cell_positions:
        if p is not None:
            yield p