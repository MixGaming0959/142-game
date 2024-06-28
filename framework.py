import sys
import os
import ctypes
import pygame
from math import ceil


class Screen():
    def __init__(self, x: int, y: int):
        # กำหนดการแบ่งหน้าจอ
        self.MAX_X = x
        self.MAX_Y = y
        # ตั้งค่าให้เต็มจอเป็นค่าเริ่มต้น
        self.set_fullscreen_mode()

    def set_fullscreen_mode(self):
        # ตั้งค่าโหมดการแสดงผลเป็นเต็มหน้าจอ
        self.window = pygame.display.set_mode((0, 0))
        pygame.display.toggle_fullscreen()
        # ตรวจจับความละเอียดหน้าจอปัจจุบัน
        self.__get_screen_info()
        # แบ่งหน้าจออกเป็น grid
        self.__set_axis()

    def set_screen(self, width: int, height: int):
        # ตั้งค่าโหมดการแสดงผลเป็นค่าที่กำหนด
        self.window = pygame.display.set_mode((width, height))
        # ตรวจจับความละเอียดหน้าจอปัจจุบัน
        self.__get_screen_info()
        # แบ่งหน้าจออกเป็น grid
        self.__set_axis()
        self.set2center_window()

    def set2center_window(self):
        # ดึงข้อมูลของจอภาพ
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        # คำนวณตำแหน่งของหน้าต่างเพื่อให้อยู่ตรงกลาง
        x = (screen_width - self.SCREEN_WIDTH) // 2
        y = (screen_height - self.SCREEN_HEIGHT) // 2

        # ตั้งค่าตำแหน่งของหน้าต่าง
        hwnd = pygame.display.get_wm_info()['window']
        user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001)

    def pack_x(self, box_x: int) -> int:
        return self.__resize2x(box_x)
    
    def pack_y(self, box_y: int) -> int:
        return self.__resize2y(box_y)
    
    def width(self, scale: int) -> int:
        return self.__resize2x(scale)
    
    def height(self, scale: int) -> int:
        return self.__resize2y(scale)
    
    def __resize2x(self, scale: int):
        scale = min(self.MAX_X, scale)
        scale = max(scale, 0)
        return ceil(self.x_axis * scale)
    
    def __resize2y(self, scale: int):
        scale = min(self.MAX_Y, scale)
        scale = max(scale, 0)
        return ceil(self.y_axis * scale)

    def __set_axis(self):
        self.x_axis = self.SCREEN_WIDTH / self.MAX_X
        self.y_axis = self.SCREEN_HEIGHT / self.MAX_Y

    def __get_screen_info(self):
        screen_info = pygame.display.Info()
        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT = screen_info.current_h


class FontSystem():
    def __init__(self,
                 font_path: str,
                 font_size: int,
                 font_color: tuple):
        if font_path is None:
            self.font_path = self.__get_font()
        else:
            self.font_path = font_path
        self.base_font_size = font_size  # เก็บขนาด font เริ่มต้น
        self.font_size = font_size
        self.font_color = font_color
        self.create_font()
    
    def create_font(self):
        # สร้าง font
        self.font = pygame.font.Font(self.font_path, self.font_size) if self.font_path else pygame.font.SysFont(None, self.font_size)
    
    def set_font_size(self, window: pygame.Surface):
        # ดึงค่าความสูงของหน้าจอออกมา
        window_height = window.get_height()
        
        # คำนวณขนาด font ใหม่ตามสัดส่วนของความสูงหน้าจอ
        # สมมติว่าเราออกแบบ UI สำหรับความสูง 720 pixels
        scale_factor = window_height / 720
        new_font_size = int(self.base_font_size * scale_factor)
        
        # ถ้าขนาด font เปลี่ยน ให้สร้าง font ใหม่
        if new_font_size != self.font_size:
            self.font_size = new_font_size
            self.create_font()
    
    def __get_font(self):
        # ตรวจสอบว่าอยู่ใน onefile mode หรือไม่
        if getattr(sys, '_MEIPASS', None):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        # สร้าง path ไปยังไฟล์ font
        return os.path.join(base_path, "Assets", "font", "Mali-Regular.ttf")


class Button(FontSystem):
    def __init__(self, 
                 text: str, 
                 font_size: int, 
                 font_color: tuple, 
                 color_button: tuple, 
                 radius=20, 
                 name_button=None, 
                 font_path=None):
        super().__init__(font_path, font_size, font_color)
        self.text = text
        if name_button is None:
            self.name_button = self.text
        self.text_surface = self.font.render(text, True, font_color)
        self.set_button()
        self.color_button = color_button
        self.radius = radius
        # สถานะทั้งหมดได้แก่ "normal", "hover", "pressed"
        self.state = "normal"  

    def show(self, 
             screen_draw: pygame.Surface, 
             width_button: int, 
             height_button: int, 
             x: int, y: int):
        self.set_font_size(screen_draw)
        self.set_button(width_button, height_button, x, y)
        button_color = self.color_button
        text_color = self.font_color
        
        # เมื่อเมาส์ลอยอยู่เหนือปุ่ม
        if self.state == "hover":
            button_color = [min(255, c + 120) for c in self.color_button] # ทำให้ปุ่มสว่างขึ้น
            text_color = [min(255, c + 20) for c in self.font_color]
        
        pygame.draw.rect(screen_draw, button_color, self.button, 0, self.radius)

        # render text surface ใหม่
        text_surface = self.font.render(self.text, True, text_color)
        
        # คำนวณตำแหน่งกึ่งกลางของปุ่มใหม่ทุกครั้ง
        text_rect = text_surface.get_rect(center=self.button.center)
        
        screen_draw.blit(text_surface, text_rect)

    def change_color_button(self, color_button: tuple):
        self.color_button = color_button

    def set_button(self, 
                   width_button=1,
                   height_button=1,
                   x=1, y=1):
        self.button = pygame.Rect(x, y, width_button, height_button)
    
    def click(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.button.collidepoint(event.pos):
                self.state = "hover"
            else:
                self.state = "normal"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.button.collidepoint(event.pos) and event.button == 1:  # ตรวจสอบว่าเป็นปุ่มซ้าย
                self.state = "pressed"
                return True  # ส่งคืนค่าว่ากดปุ่มซ้ายแล้ว
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.state == "pressed":
                self.state = "normal"
        return False


class ImageButton(Button):
    def __init__(self, 
                 text: str, 
                 font_size: int, 
                 font_color: tuple, 
                 image_path: str, 
                 name_button=None,
                 font_path=None):
        super().__init__(text, font_size, font_color, (0, 0, 0), 0, name_button, font_path)  # ส่งค่าที่ไม่ใช้ไปยัง super
        self.image = pygame.image.load(image_path).convert_alpha()
        self.original_image = self.image.copy()  # เก็บสำเนาภาพเดิมเพื่อการทำให้สว่างขึ้น
        self.image_rect = self.image.get_rect()

    def lighten_image(self, image, amount=50):
        """เพิ่มความสว่างให้กับรูปภาพ"""
        lighten = pygame.Surface(image.get_size()).convert_alpha()
        lighten.fill((amount, amount, amount, 0))
        lightened_image = image.copy()
        lightened_image.blit(lighten, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return lightened_image

    def show(self, 
             screen_draw: pygame.Surface, 
             width_button: int, 
             height_button: int, 
             x: int, y: int):
        self.set_font_size(screen_draw)
        self.set_button(width_button, height_button, x, y)
        self.image = pygame.transform.scale(self.original_image, (width_button, height_button))
        text_color = self.font_color
        image = self.image
        
        # เมื่อเมาส์ลอยอยู่เหนือปุ่ม
        if self.state == "hover":
            image = self.lighten_image(self.image)  # ทำให้ปุ่มสว่างขึ้น

        # วาดรูปภาพลงบนปุ่ม
        self.image_rect = image.get_rect(topleft=(x, y))
        screen_draw.blit(image, self.image_rect)

        # วาดข้อความบนปุ่ม
        screen_draw.blit(self.font.render(self.text, True, text_color), self.text_rect)

    def set_button(self, 
                   width_button=1,
                   height_button=1,
                   x=1, y=1):
        self.image_rect = pygame.Rect(x, y, width_button, height_button)
        self.text_rect = self.text_surface.get_rect(center=self.image_rect.center)
        self.button = self.image_rect


class Text(FontSystem):
    def __init__(self, 
                 text_default: str, 
                 font_size: int, 
                 font_color: tuple, 
                 font_path=None):
        super().__init__(font_path, font_size, font_color)
        # สร้างออบเจกต์ Text สำหรับแสดงข้อความบนหน้าจอ
        self.text = text_default

    def show(self, 
             screen_draw: pygame.Surface, 
             x: int, y: int,
             text=None,
             center_mode=False):
        self.set_font_size(screen_draw)
        if text is not None:
            self.text = text
        text_surface = self.font.render(self.text, True, self.font_color)
        if center_mode:
            text_rect = text_surface.get_rect()  # สร้าง text_rect ก่อน
            text_rect.centerx = x  # กำหนดตำแหน่งกึ่งกลางในแนวแกน x
            text_rect.top = y     # กำหนดตำแหน่ง y ตามที่ต้องการ
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        screen_draw.blit(text_surface, text_rect)


class Dropdown(FontSystem):
    def __init__(self, 
                 options: list, 
                 font_size: int,
                 font_color: tuple, 
                 color_dropdown: tuple, 
                 font_path=None):
        super().__init__(font_path, font_size, font_color)
        self.__options = options
        self.__color_dropdown = color_dropdown
        self.__active = False
        self.selected_option = options[0]
        # สถานะทั้งหมดได้แก่ "normal", "hover"
        self.__hover_option = "normal."

    def show(self,
             screen_draw: pygame.Surface, 
             width: int, 
             height: int, 
             x: int, y: int):
        self.set_font_size(screen_draw)
        self.rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen_draw, self.__color_dropdown, self.rect)
        text_surface = self.font.render(self.selected_option if self.selected_option else self.__options[0], True, self.font_color)
        text_rect = text_surface.get_rect(center=(x+(width/2)-10, y+(height/2)))
        screen_draw.blit(text_surface, text_rect)

        # วาดลูกศรชี้ลง (หรือชี้ขึ้นถ้า Dropdown เปิดอยู่)
        arrow_direction = 1 if self.__active else -1
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5 * arrow_direction),
            (self.rect.right - 10, self.rect.centery + 5 * arrow_direction),
            (self.rect.right - 30, self.rect.centery + 5 * arrow_direction)
        ]
        pygame.draw.polygon(screen_draw, self.font_color, arrow_points)

        if self.__active:
            for i, option in enumerate(self.__options):
                rect = pygame.Rect(self.rect.x, self.rect.y + (i+1) * self.rect.height, self.rect.width, self.rect.height)
                if self.__hover_option == i:
                    color_dropdown = [min(255, c + 20) for c in self.__color_dropdown] # ทำให้สว่างขึ้น
                else:
                    color_dropdown = [max(0, c - 55) for c in self.__color_dropdown] # ทำให้มืดลง
                pygame.draw.rect(screen_draw, color_dropdown, rect)
                text_surface = self.font.render(option, True, self.font_color)
                text_rect = text_surface.get_rect(center=(rect.x+(width/2), rect.y+(height/2)))
                screen_draw.blit(text_surface, text_rect)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION and self.__active:
            for i, option in enumerate(self.__options):
                rect = pygame.Rect(self.rect.x, self.rect.y + (i+1) * self.rect.height, self.rect.width, self.rect.height)
                if rect.collidepoint(event.pos):
                    self.__hover_option = i
                    break
                else:
                    self.__hover_option = -1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.__active = not self.__active
            elif self.__active:
                for i, option in enumerate(self.__options):
                    rect = pygame.Rect(self.rect.x, self.rect.y + (i+1) * self.rect.height, self.rect.width, self.rect.height)
                    if rect.collidepoint(event.pos):
                        self.selected_option = option
                        self.__active = False
                        # ส่งคืนค่า True เมื่อมีการเลือกตัวเลือก
                        return True
                    else:
                        self.__active = False
        # ส่งคืนค่า False เมื่อไม่มีการเลือกตัวเลือกใด ๆ
        return False