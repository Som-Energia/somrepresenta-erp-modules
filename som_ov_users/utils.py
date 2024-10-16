
class OrmLink:
    # (0, 0, { values }) link to a new record that needs to be created with the given values dictionary
    create = 0
    # (1, ID, { values }) update the linked record with id = ID (write values on it)
    update = 1
    # (2, ID) remove and delete the linked record with id = ID (calls unlink on ID, that will delete the object completely, and the link to it as well)
    delete = 2
    # (3, ID) cut the link to the linked record with id = ID (delete the relationship between the two objects but does not delete the target object itself)
    unlink = 3
    # (4, ID) link to existing record with id = ID (adds a relationship)
    link = 4
    # (5) unlink all (like using (3,ID) for all linked records)
    clear = 5
    # (6, 0, [IDs]) replace the list of linked IDs (like using (5) then (4,ID) for each ID in the list of IDs)
    set = 6


class Many2Many:
    @staticmethod
    def create(values):
        return OrmLink.create, values

    @staticmethod
    def update(id, data):
        return OrmLink.update, id, values

    @staticmethod
    def delete(id):
        """Deletes the link and the linked object"""
        return OrmLink.delete, id

    @staticmethod
    def unlink(id):
        """Removes the link keeping the linked object"""
        return OrmLink.unlink, id

    @staticmethod
    def link(id):
        """Add a link to an existing object"""
        return OrmLink.link, id

    @staticmethod
    def clear():
        """Clear any existing links keeping existing objects"""
        return (OrmLink.clear,)


    @staticmethod
    def set(ids):
        """Replace existing links with provided ids"""
        return OrmLink.set, 0, ids

