def get_area_type(area_number: int) -> str:
    if area_number < 34:
        return 'кран'
    else:
        return 'ричстакер'
