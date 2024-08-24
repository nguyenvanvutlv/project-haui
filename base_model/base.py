import flet as ft
from flet_route import Params, Basket
from abc import abstractmethod

class Field:
    def __init__(self, default=None):
        self.default = default
        self.name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self  # Trả về chính đối tượng Field nếu truy cập từ lớp
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        fields = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                fields[key] = value
        dct['_fields'] = fields
        dct['_id_counter'] = 0  # Biến lớp để theo dõi ID tự động tăng
        return super().__new__(cls, name, bases, dct)


class Model(metaclass=ModelMeta):
    def __init__(self):
        self.id = self._get_next_id()  # Gán ID tự động tăng cho đối tượng
        for name, field in self._fields.items():
            if not hasattr(self, name):
                setattr(self, name, field)

    @classmethod
    def _get_next_id(cls):
        cls._id_counter += 1
        return cls._id_counter

    def save(self):
        data = {name: getattr(self, name) for name in self._fields}
        data['id'] = self.id
        # print(f"Lưu {self.__class__.__name__} với dữ liệu: {data}")

    @abstractmethod
    def create_object(self, **kwargs):
        return self

class MainApp(Model):
    pass

class MainApp(Model):
    page: ft.Page = None
    list_record = None

    @abstractmethod
    def create_object(self, **kwargs) -> MainApp:
        self.page: ft.Page = kwargs.get('page')
        return self

    def settings_windows(self, width: int, height: int):
        self.page.window.width = width
        self.page.window.height = height
        self.page.update()

class BaseLayout(Model):
    appbar: ft.AppBar = None
    main_app: MainApp = None

    def create_object(self, **kwargs):
        self.main_app = kwargs.get('main_app')
        self.appbar = self.create_appbar(
            title = kwargs.get('title', ''),
            icons = kwargs.get('icons', []),
            tooltips = kwargs.get('tooltips', []),
            func = kwargs.get('func', [])
        )
        return self

    @abstractmethod
    def create_appbar(self, title: str, icons: list = [],
                      func: list = [], tooltips: list = []) -> ft.AppBar:
        appbar = ft.AppBar(
            title = ft.Text(title),
            actions = [
                ft.IconButton(icon, tooltip = tooltips[index],
                              on_click = func[index]) \
                for index, icon in enumerate(icons)
            ]
        )
        return appbar


    @abstractmethod
    def view(self, page: ft.Page, params: Params, basket: Basket):
        base_view: ft.View = ft.View(
            route = page.route,
            controls = [
                self.appbar
            ]
        )
        return base_view






