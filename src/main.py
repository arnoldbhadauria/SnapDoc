import io
import flet as ft
from PIL import Image
import random

# web images (for testing purpose) - https://picsum.photos/150/150?{i} 

def main(page: ft.Page):
    page.title = "SnapDoc"
    page.theme_mode = ft.ThemeMode.DARK

    my_color = ft.Colors.BLUE
    white_color = ft.Colors.WHITE
    dark_color = ft.Colors.BLUE_GREY_900

    default_border = ft.Border.all(1,white_color)

    pr = ft.ProgressBar(width=5000,color=my_color,visible=False,value=None)

    # app_data_path = os.getenv("FLET_APP_STORAGE_DATA")

    files = []

    def show_error(message):
        error_snackbar = ft.SnackBar(
            content=ft.Text(f"{message}",color=white_color),
            bgcolor=ft.Colors.RED
            
        )
        page.show_dialog(error_snackbar)
        page.update()

    def show_info(message):
        info_snackbar = ft.SnackBar(
            content=ft.Text(f"{message}",color=white_color),
            bgcolor=ft.Colors.GREEN
            
        )
        page.show_dialog(info_snackbar)
        page.update()


    print("Initial route:", page.route)

    def remove_image(container,file_obj):
        if container in image_grid.controls:
            image_grid.controls.remove(container)

        if file_obj in files:
            files.remove(file_obj)

        if len(files) == 0:
            clear_all_btn.disabled = True

        page.update()


    async def handle_pick_files(e: ft.Event[ft.Button]):
        pr.visible = True
        page.update()

        picked_files = await ft.FilePicker().pick_files(
            allow_multiple=True,
            with_data=True
        )
        image_grid.controls.clear()
        files.clear()

        if not picked_files:
            pr.visible=False
            page.update()
            print("User cancelled file selection")
            return

        for obj in picked_files:
            files.append(obj)
       

        for obj in files:
            
            remove_btn = ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_color=white_color,
                bgcolor=ft.Colors.BLACK_54,
                icon_size=13,
                width=30,
                height=30,
                # on_click=remov
            )
            
            image_container = ft.Container(
                ft.Stack(
                    width=150,
                    height=150,
                    controls=[
                        ft.Image(
                            src=obj.path,
                            fit=ft.BoxFit.COVER,
                            repeat=ft.ImageRepeat.NO_REPEAT,
                            border_radius=ft.BorderRadius.all(10),
                            width=150,
                            height=150
                        ),
                        remove_btn
                        
                    ],
                ),
                width=150,
                height=150,
                # border=ft.Border.all(0.5,white_color),
                # border_radius=10,
                # padding=10
            )
            remove_btn.on_click = lambda _, c=image_container,f=obj: remove_image(c,f)

            image_grid.controls.append(image_container)
                
        clear_all_btn.disabled = False
        pr.visible = False
        page.update()


    def clear_grid_view():
        image_grid.controls.clear()
        files.clear()
        clear_all_btn.disabled = True
        page.update()

    image_grid = ft.GridView(
            expand=1,
            run_spacing=5,
            spacing=5,
            runs_count=2,
            max_extent=150,
            child_aspect_ratio=1.0,
            controls=[
                
            ],
            padding=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    clear_all_btn = ft.TextButton(
        ft.Text("Clear all",size=13),
        disabled=True,
        on_click=clear_grid_view
    )

    async def convert_to_pdf(e):        
        try:
            # Check karein ki files select hui hain ya nahi
            if not files: 
                show_error("No image selected.")
                return
            
            pr.visible = True
            page.update()
            
            image_list = []

            for f in files:
                # FIX 1: f.bytes check karein
                if f.bytes is None or len(f.bytes) == 0:
                    print(f"Skipping {f.name}: bytes are empty.")
                    continue

                # Bytes ko Image mein convert karein
                # Hum io.BytesIO use karte hain taaki Pillow bytes read kar sake
                img = Image.open(io.BytesIO(f.bytes))

                img.thumbnail((1024, 1024))

                # PDF requires RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")

                image_list.append(img)

            if not image_list:
                show_error("Could not read any images.")
                pr.visible=False
                page.update()
                return

            # PDF Conversion (In-memory)
            pdf_buffer = io.BytesIO()
            
            first_image = image_list[0]
            remaining_images = image_list[1:]

            # Images ko PDF form mein buffer mein save karein
            first_image.save(
                pdf_buffer, 
                format="PDF", 
                save_all=True, 
                append_images=remaining_images
            )
            
            # Buffer se bytes nikalein Flet ke liye
            pdf_bytes = pdf_buffer.getvalue() 
            pdf_buffer.close()

            # FIX 2: Save dialog kholna globally defined picker se
            # Naya ft.FilePicker() use mat karein
            # 'src_bytes' pass karna zaroori hai!
            save_path = await ft.FilePicker().save_file(
                allowed_extensions=["pdf"],
                file_name=f"snapdoc_{random.randint(100000,999999)}.pdf",
                src_bytes=pdf_bytes # PDF ka content yahan ja raha hai
            )

            if save_path:
                show_info("File saved successfully.")
            else:
                # User cancelled save dialog
                print("Save cancelled.")

        except Exception as ex:
            show_error(f"Error during conversion: {str(ex)}")

        pr.visible=False
        page.update()
        
        # finally:
        #     convert_btn.disabled = False
        #     page.update()
        

    def route_change():
        print("Route change:", page.route)
        page.views.clear()

        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(
                        title=ft.Text("SnapDoc",weight=ft.FontWeight.W_500),
                        bgcolor=my_color,
                        
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Text("All Images",expand=True,size=13),
                                            clear_all_btn
                                        ]
                                    ),
                                    padding=7,
                                    # border=default_border,
                                    bgcolor=dark_color
                                ),
                                pr,
                                image_grid,
                            ],
                            spacing=0,
                            expand=True
                        ),
                        expand=True
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.FilledButton(
                                    ft.Text("Select images",color=white_color),
                                    icon=ft.Icons.IMAGE,
                                    icon_color=white_color,
                                    bgcolor=dark_color,
                                    width=400,
                                    height=40,
                                    align=ft.Alignment.CENTER,
                                    on_click=handle_pick_files
                                ),
                                ft.FilledButton(
                                    ft.Text("Convert to PDF",color=white_color),
                                    icon=ft.Icons.PICTURE_AS_PDF,
                                    icon_color=white_color,
                                    bgcolor=my_color,
                                    width=400,
                                    height=40,
                                    align=ft.Alignment.CENTER,
                                    on_click=convert_to_pdf
                                )
                            ],
                        ),
                        padding=20,
                        alignment=ft.Alignment.CENTER
                    )
                ],
                spacing=0,
                padding=0
            )
        )
        # if page.route == "/saved_pdfs":
        #     available_pdfs = os.listdir(app_data_path)

        #     page.views.append(
        #         ft.View(
        #             route="/saved_pdfs",
        #             controls=[
        #                 ft.AppBar(
        #                     title=ft.Text("Saved Files",color=my_color),
        #                 ),
        #                 ft.Container(
        #                     content=ft.Column(
        #                         controls=[
        #                             ft.Container(
        #                                 content=ft.Row(
        #                                     controls=[
        #                                         ft.Icon(
        #                                             icon=ft.Icons.PICTURE_AS_PDF,
        #                                             color=ft.Colors.RED,
        #                                             size=30
        #                                         ),
        #                                         ft.Container(
        #                                             content=ft.Column(
        #                                                 controls=[
        #                                                     ft.Text(f"i")
        #                                                 ],
        #                                                 align=ft.Alignment.CENTER
        #                                             ),
        #                                             alignment=ft.Alignment.CENTER,
        #                                             padding=10,
        #                                             # border_radius=10
        #                                         )
        #                                     ]
        #                                 ),
        #                                 height=70,
        #                                 # border=default_border,
        #                                 border_radius=10,
        #                                 padding=10,
        #                                 bgcolor=dark_color,
        #                             ) for i in available_pdfs
        #                         ],
        #                         expand=True,
        #                         scroll=ft.ScrollMode.AUTO,
        #                     ),
        #                     expand=True,
        #                     border=default_border,
        #                     padding=10
        #                 )
                        
        #             ],
        #             padding=0
        #         )
        #     )
        # if page.route == "/settings/mail":
        #     page.views.append(
        #         ft.View(
        #             route="/settings/mail",
        #             controls=[
        #                 ft.AppBar(
        #                     title=ft.Text("Mail Settings"),
        #                     bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        #                 ),
        #                 ft.Text("Mail settings!"),
        #             ],
        #             padding=0
        #         )
        #     )
        page.update()

    async def view_pop(e):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()


if __name__ == "__main__":
    ft.run(main,assets_dir="assets",upload_dir="uploads")