import flet as ft

class Item(ft.Column):
    def __init__(self, item_name, item_price, item_quantity):
        super().__init__()
        self.completed = False
        self.bought = False
        self.item_name = item_name
        self.item_status_change = None
        self.item_bought_change = None
        self.item_delete = None
        self.display_item = ft.Checkbox(value=False, label=self.item_name, on_change=self.status_changed)
        self.bought_item = ft.Checkbox(value=False, label="bought", on_change = self.bought_changed)
        self.quantity = ft.TextField(value=item_quantity, text_align= "right", width = 50, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$",replacement_string=""))
        self.price = ft.TextField(value=item_price, text_align="right", width=70, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$",replacement_string=""))
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_item,
                ft.Row(
                    spacing=0,
                    controls=[
                        self.bought_item,
                        ft.Row(
                            [
                                ft.IconButton(ft.icons.REMOVE, on_click=self.minus_clicked),
                                self.quantity,
                                ft.IconButton(ft.icons.ADD, on_click=self.plus_clicked),
                            ],
                        ),
                        self.price,
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit Shop",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete Shop",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )
        self.edit_view = ft.Row(
            visible = False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update Shop",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def functioner(self, item_status_change, item_bought_change, item_delete):
        self.item_status_change = item_status_change
        self.item_bought_change = item_bought_change
        self.item_delete = item_delete

    def status_changed(self, e):
        self.completed = self.display_item.value
        self.item_status_change()

    def bought_changed(self, e):
        self.bought = self.bought_item.value
        self.item_bought_change()
    def edit_clicked(self,e):
        self.edit_name.value = self.display_item.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        if self.page.client_storage.contains_key(self.item_name):
            self.page.client_storage.remove(self.item_name)
        self.display_item.label = self.edit_name.value
        self.item_name = self.edit_name.value
        self.page.client_storage.set(self.item_name, [self.item_name, self.price.value, self.quantity.value])
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def delete_clicked(self, e):
        self.item_delete(self)

    def minus_clicked(self, e):
        self.quantity.value = str(float(self.quantity.value)-1.0)
        self.update()

    def plus_clicked(self, e):
        self.quantity.value = str(float(self.quantity.value)+1.0)
        self.update()

class ShopApp(ft.Column):
    def __init__(self):
        super().__init__()
        self.new_item = ft.TextField(hint_text="What needs to be bought", on_submit=self.add_clicked, expand = True)
        self.new_price=ft.TextField(value="0", text_align= "right", width = 50, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$",replacement_string=""))
        self.new_quantity=ft.TextField(value="0.00", text_align="right", width=70, input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d*$",replacement_string=""))
        self.items_view = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="unselected"), ft.Tab(text="to buy"), ft.Tab("bought")],
        )

        self.items_left = ft.Text("0 items left")

        self.width = 600
        self.controls = [
            ft.Row(
                [ft.Text(value="Items", theme_style = ft.TextThemeStyle.HEADLINE_MEDIUM)],
                alignment = ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    self.new_item,
                    ft.FloatingActionButton(
                        icon=ft.icons.ADD, on_click = self.add_clicked
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls = [
                    self.filter,
                    self.items_view,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text="Clear completed", on_click=self.clear_clicked
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def did_mount(self):
        key_list = self.page.client_storage.get_keys("")
        if len(key_list) > 0:
            for thing in key_list:
                load_elements = self.page.client_storage.get(thing)
                load_item = Item(load_elements[0], load_elements[1], load_elements[2])
                load_item.functioner(self.item_status_change, self.item_bought_change, self.item_delete)
                self.items_view.controls.append(load_item)
                self.update()


    def before_update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        cur_value = 0.0
        total = 0.0
        for item in self.items_view.controls:
            item.visible = (
                status == "all"
                or (status == "unselected" and item.completed == False and item.bought == False)
                or (status == "to buy" and item.completed and item.bought == False)
                or (status == "bought" and item.completed and item.bought)
            )
            if item.completed and not item.bought:
                count += 1
                total += float(item.quantity.value) * float(item.price.value)
            elif item.completed and item.bought:
                total += float(item.quantity.value) * float(item.price.value)
                cur_value += float(item.quantity.value) * float(item.price.value)
            self.items_left.value = f"{count} items to be bought\nCurrent basket value {cur_value}\nTotal basket value {total}"
            self.page.client_storage.set(item.item_name, [item.item_name, item.price.value, item.quantity.value])

    def tabs_changed(self, e):
        self.update()

    def item_status_change(self, e):
        self.update()

    def item_bought_change(self, e):
        self.update()

    def add_clicked(self, e):
        if self.new_item.value:
            item = Item(self.new_item.value, self.new_price.value, self.new_quantity.value)
            item.functioner(self.item_status_change, self.item_bought_change, self.item_delete)
            self.items_view.controls.append(item)
            self.new_item.value = ""
            self.new_item.focus()
            self.update()

    def item_delete(self, item):
        if self.page.client_storage.contains_key(item.item_name):
            self.page.client_storage.remove(item.item_name)
        self.items_view.controls.remove(item)
        self.update()

    def clear_clicked(self, e):
        for item in self.items_view.controls[:]:
            if item.completed:
                self.item_delete(item)
def main(page: ft.Page):
    page.title= "Shopping App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.add(ShopApp())



ft.app(main)