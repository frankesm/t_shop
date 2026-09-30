class GenericController:
    title = ""
    manager_class = None
    serializer_class = None
    ui_class = None

    def get_manager_class(self, action=None):
        return self.manager_class

    def get_serializer_class(self, action=None):
        return self.serializer_class

    def build_ui(self):
        return self.ui_class(controller=self)

    def get_or_fail(self, manager, pk):
        obj = manager.retrieve(pk)
        if obj is None:
            raise Exception("El registro no existe.")
        return obj
