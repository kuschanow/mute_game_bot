def enum_to_choices(enum_class):
    return [(tag.value, tag.name.capitalize()) for tag in enum_class]
