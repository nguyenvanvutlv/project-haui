from templates.view.home import HomeView
from base.system import MainApp


class HomeControls(HomeView):
    def __init__(self, main_app : MainApp):
        super(HomeControls, self).__init__(main_app)