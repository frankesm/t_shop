class Router:
    def __init__(self):
        self.controllers = []

    def register(self, controller_class):
        self.controllers.append(controller_class())


router = Router()
# router.register()
