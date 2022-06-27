# -*- coding: utf-8 -*-

from tkinter.ttk import Label, Scrollbar, Treeview, Entry, Combobox, Style

from tkinter  import Tk, Frame, Toplevel, Button, Checkbutton
from tkinter  import StringVar, BooleanVar
from tkinter  import GROOVE, FLAT, DISABLED, NORMAL
from tkinter  import LEFT, RIGHT
from tkinter  import TOP, BOTTOM, CENTER
from tkinter  import X, Y, BOTH, END
from database import DataBase

from re import search, fullmatch


class Aibolit(Frame): # ГЛАВНЫЙ КЛАСС;
    def __init__(self, root, x, y, w, h):
        super().__init__(root)
        self.x = x
        self.y = y
        self.w = w
        self.h = 60
        self.tg = ('str_odd', 'str_even')
        self.init_main()
        self.db = db
        self.update_records()

    def init_main(self):
        # СТИЛЬ ШРИФТА + ПАЛИТРА ЦВЕТОВ;
        self.font  = ('Consolas', '10')
        self.color = [
            '#303841', # 0. dark gray
            '#3A4750', # 1. light gray
            '#D72323', # 2. light red
            '#EEEEEE', # 3. gray
            '#FAFAFA', # 4. white
            '#D4D4D4', # 5. darklight gray
            '#ab1b1b', # 6. dark red
        ]
        # ТОЛБЦЫ, ШИРИНА СТОЛБЦОВ и НАЗВАНИЯ СТОЛБЦОВ Treeview;
        COLS = ('id', 'status', 'number', 'author', 'datetime')
        TREE_WIDTH = [50, 30, 80, 80, 170]
        TREE_TITLE = ['ID', '☰', '№Заявки', '№Аптеки', 'Дата']

        # ФОН ОКНА
        self['bg'] = self.color[0]

        # СТИЛЬ ТАБЛИЦ и КНОПОК в ВСПЛЫВАЮЩИХ ОКНАХ;
        Style().configure('Treeview', font=self.font, foreground=self.color[0])
        Style().configure('Treeview.Heading', font=self.font, foreground=self.color[0])
        Style().configure('My.TLabel', font=self.font, background=self.color[0], foreground=self.color[4])
        
        # ВЕРХНЯЯ и НИЖНЯЯ ПАНЕЛЬ для КНОПОК и ПОДСКАЗОК;
        TB_TOP = Frame(self, bg=self.color[0], bd=1)
        TB_MID = Frame(self, bg=self.color[0], bd=1)
        TB_BOT = Frame(self, bg=self.color[0], bd=1)

        TB_TOP.pack(side=TOP, fill=X)
        TB_MID.pack(fill=X, padx=3)
        TB_BOT.pack(side=BOTTOM, fill=X)

        # КНОПКИ на ВЕРХНЕЙ ПАНЕЛИ;
        BTNADD = Button(TB_TOP, text='ДОБАВИТЬ', width=5, height=1, compound=TOP, command=self.open_dlg_add,
                        font=self.font, fg=self.color[4], bg=self.color[0], activebackground=self.color[1],
                        activeforeground=self.color[3], relief=GROOVE, overrelief=GROOVE)
        BTNEDT = Button(TB_TOP, text='РЕДАКТИРОВАТЬ', width=5, height=1, compound=TOP, command=self.open_dlg_edit,
                        font=self.font, fg=self.color[4], bg=self.color[0], activebackground=self.color[1],
                        activeforeground=self.color[3], relief=GROOVE, overrelief=GROOVE)
        BTNDEL = Button(TB_TOP, text='УДАЛИТЬ', width=5, height=1, compound=TOP, command=self.open_dlg_del,
                        font=self.font, fg=self.color[3], bg=self.color[6], activebackground=self.color[2],
                        activeforeground=self.color[3], relief=GROOVE, overrelief=GROOVE)
        BTNSRH = Button(TB_TOP, text='◯', width=3, height=1, compound=TOP, command=self.open_dlg_search,
                        font=self.font, fg=self.color[4], bg=self.color[0], activebackground=self.color[1],
                        activeforeground=self.color[3], relief=GROOVE, overrelief=GROOVE)

        BTNADD.pack(side=LEFT, fill=X, expand=1)
        BTNEDT.pack(side=LEFT, fill=X, expand=1)
        BTNDEL.pack(side=LEFT, fill=X, expand=1)
        BTNSRH.pack(side=LEFT, fill=X)

        BTNADD.bind('<Enter>', lambda event: BTNADD.configure(bg=self.color[1]))
        BTNADD.bind('<Leave>', lambda event: BTNADD.configure(bg=self.color[0]))
        BTNEDT.bind('<Enter>', lambda event: BTNEDT.configure(bg=self.color[1]))
        BTNEDT.bind('<Leave>', lambda event: BTNEDT.configure(bg=self.color[0]))
        BTNDEL.bind('<Enter>', lambda event: BTNDEL.configure(bg=self.color[2]))
        BTNDEL.bind('<Leave>', lambda event: BTNDEL.configure(bg=self.color[6]))
        BTNSRH.bind('<Enter>', lambda event: BTNSRH.configure(bg=self.color[1]))
        BTNSRH.bind('<Leave>', lambda event: BTNSRH.configure(bg=self.color[0]))

        # ВЫВОД ОШИБОК и КОЛ-ВА ЗАПИСЕЙ на НИЖНЮЮ ПАНЕЛЬ;
        self.error = Label(TB_BOT, style='My.TLabel', foreground=self.color[2])
        self.count = Label(TB_BOT, style='My.TLabel')
        self.error.pack(side=RIGHT)
        self.count.pack(side=LEFT)

        # ПОЛОСЫ ПРОКРУТКИ и ТАБЛИЦА;
        _yscroll_ = Scrollbar(TB_MID)
        self.tree = Treeview(TB_MID, columns=COLS, height=22, show='headings',
                             yscrollcommand=_yscroll_.set, style='My.Treeview')
        _yscroll_.config(command=self.tree.yview)

        for i in range(len(COLS)):
            if i % 2 != 0: self.tree.column(COLS[i], anchor=CENTER)
            self.tree.column(COLS[i], width=TREE_WIDTH[i], stretch=True, minwidth=TREE_WIDTH[i])
            self.tree.heading(COLS[i], text=TREE_TITLE[i])

        # УСТАНАВЛИВАЕМ ТЕГИ для ПОКРАСКИ СТРОК;
        self.tree.tag_configure(self.tg[0], background=self.color[3])
        self.tree.tag_configure(self.tg[1], background=self.color[5])

        _yscroll_.pack(side=RIGHT, fill=Y)
        self.tree.pack()
        self.tree.bind('<Button-1>', lambda event: 'break' if self.tree.identify_region(event.x, event.y) == 'separator' else None)

    def update_records(self): # ОБНОВЛЕНИЕ ДАННЫХ;
        count = 0
        self.db.c.execute(''' SELECT * FROM data ''')
        [ self.tree.delete(item) for item in self.tree.get_children() ]
        for row in self.db.c.fetchall():
            if count % 2 != 0: self.tree.insert('', 'end', values=row, tags=self.tg[0])
            if count % 2 == 0: self.tree.insert('', 'end', values=row, tags=self.tg[1])
            count += 1
        self.count.configure(text='Количество записей: %d' % (count))
        self.db.conn.commit()

    def add_record(self, number, author): # ДОБАВЛЕНИЕ;
        if number.isdigit():
            number = int(number)
            if (number != '' and author != ''):
                self.error.configure(text='')
                flag_record = False
                self.db.c.execute(''' SELECT number FROM data ''')
                for row in self.db.c.fetchall(): # Проверка на схожую запись;
                    if (number == row[0]): flag_record = True
                if (not flag_record):
                    self.db.add_data(number, author)
                    self.error.configure(text='Заявка добавлена!')
                    self.update_records()
                else: self.error.configure(text='Номер заявки существует!')
            else: self.error.configure(text='Данные не введены в поле!')
        else: self.error.configure(text='Введите числовые значения!')
    
    def edit_record(self, number, author, datatime): # РЕДАКТИРОВАНИЕ;
        if (number != ''):
            self.error.configure(text='')
            self.db.c.execute(''' UPDATE data SET number=?, author=?, datetime=? WHERE id=? ''',
                              (number, author, datatime, self.tree.set(self.tree.selection()[0], '#1')))
            self.db.conn.commit()
            self.update_records()
        else: self.error.configure(text='Данные не введены в поле!')

    def delete_record(self): # УДАЛЕНИЕ;
        for item in self.tree.selection():
            #self.db.c.execute(''' DELETE FROM data WHERE id=? ''', (self.tree.set(item)['id'],))
            self.db.c.execute(''' UPDATE data SET status=? WHERE id=? ''', ('❎', self.tree.set(item)['id']))
        self.db.conn.commit()
        self.update_records()

    def search_record(self, states, entries): # ПОИСК;
        list_vars = []
        list_name = ['status', 'number', 'author', 'datetime']

        for i in range(len(list_name)):
           if states[i] == True and entries[i] != '':
               if list_name[i] == 'number' or list_name[i] == 'author':
                   list_vars.append((list_name[i], int(entries[i])))
               else: list_vars.append((list_name[i], entries[i]))
        if len(list_vars) == 0:
            self.error.configure(text='Поиск не выполнен!')
        else:
            self.error.configure(text='')
            count = 0
            [ self.tree.delete(item) for item in self.tree.get_children() ]
            for row in self.db.c.fetchall():
                if count % 2 != 0: self.tree.insert('', 'end', values=row, tags=self.tg[0])
                if count % 2 == 0: self.tree.insert('', 'end', values=row, tags=self.tg[1])
                count += 1
            self.count.configure(text='Количество записей: %d' % (count))
            self.db.conn.commit()

    def open_dlg_add(self): # ОТКРЫВАЕМ ОКНО ДОБАВЛЕНИЯ;
        self.error.configure(text='')
        AddData(self.x, self.y, self.w, self.h)

    def open_dlg_edit(self): # ОТКРЫВАЕМ ОКНО РЕДАКТИРОВАНИЯ;
        if self.tree.selection():
            self.error.configure(text='')
            val___name = self.tree.item(self.tree.selection()[0])['values'][2]
            val_author = self.tree.item(self.tree.selection()[0])['values'][3]
            val___data = self.tree.item(self.tree.selection()[0])['values'][4]
            EditData(self.x, self.y, self.w, self.h, val___name, val_author, val___data)
        else: self.error.configure(text='Выберите запись для редактирования!')

    def open_dlg_del(self): # ОТКРЫВАЕМ ОКНО УДАЛЕНИЯ;
        if self.tree.selection():
            self.error.configure(text='')
            self.delete_record()
        else: self.error.configure(text='Выберите запись для удаления!')

    def open_dlg_search(self): # ОТКРЫВАЕМ ОКНО ПОИСКА;
        self.error.configure(text='')
        SearchData(self.x, self.y, self.w, self.h)


class PopupFrame(Toplevel): # ОПРЕДЕЛЯЕМ ГЛАВНОЕ ОКНО для РАБОТЫ С ДАННЫМИ;
    def __init__(self):
        super().__init__(root)
        self.init_frame()
        self.view = appl
        self.w_pf = 300
        self.h_pf = 250

    def init_frame(self):
        self.f = ('Consolas', '10')
        self.c = [
            '#303841', # 0. dark gray
            '#3A4750', # 1. light gray
            '#D72323', # 2. light red
            '#EEEEEE', # 3. gray
            '#FAFAFA', # 4. white
            '#D4D4D4', # 5. darklight gray
            '#ab1b1b', # 6. dark red
        ]
        self['bg'] = self.c[0]
        self.iconbitmap('data/ai.ico')
        self.resizable(False, False)

        # ВЫСТАВЛЯЕМ НА ПОЛЕ ВСЕ ОБЪЕКТЫ;
        self.FRMID = Frame(self, bg=self.c[0], bd=1)

        # MAX ДЛИНА символов в поле, СОСТОЯНИЯ КНОПОК;
        self.len___name = StringVar()
        self.len_author = StringVar()
        self.len___data = StringVar()
        self.state_1 = BooleanVar()
        self.state_2 = BooleanVar()
        self.state_3 = BooleanVar()
        self.state_4 = BooleanVar()

        # МЕТКИ;
        self.chars_status = Label(self.FRMID, style='My.TLabel', text='Статус')
        self.chars___name = Label(self.FRMID, style='My.TLabel', text='Номер заявки')
        self.chars_author = Label(self.FRMID, style='My.TLabel', text='Номер аптеки')
        self.chars___data = Label(self.FRMID, style='My.TLabel', text='Дата')

        # ПРОВЕРКА НАЛИЧИЯ ДАННЫХ В ПОЛЯХ;
        self.CHECK_1 = Checkbutton(self.chars_status, font=self.f, fg=self.c[3], bg=self.c[0], selectcolor=self.c[0],
                                   activebackground=self.c[0], disabledforeground=self.c[3], activeforeground=self.c[3],
                                   var=self.state_1, text=' '*5, state=DISABLED)
        self.CHECK_2 = Checkbutton(self.chars___name, font=self.f, fg=self.c[3], bg=self.c[0], selectcolor=self.c[0],
                                   activebackground=self.c[0], disabledforeground=self.c[3], activeforeground=self.c[3],
                                   var=self.state_2, text='00/06', state=DISABLED)
        self.CHECK_3 = Checkbutton(self.chars_author, font=self.f, fg=self.c[3], bg=self.c[0], selectcolor=self.c[0],
                                   activebackground=self.c[0], disabledforeground=self.c[3], activeforeground=self.c[3],
                                   var=self.state_3, text='00/03', state=DISABLED)
        self.CHECK_4 = Checkbutton(self.chars___data, font=self.f, fg=self.c[3], bg=self.c[0], selectcolor=self.c[0],
                                   activebackground=self.c[0], disabledforeground=self.c[3], activeforeground=self.c[3],
                                   var=self.state_4, text='00/21', state=DISABLED)

        # Текстовые поля ENTRY, COMBOBOX
        self.combobox = Combobox(self.FRMID, font=self.f, values=('✅', '❎'))
        self.E___name = Entry(self.FRMID, font=self.f, textvariable=self.len___name)
        self.E_author = Entry(self.FRMID, font=self.f, textvariable=self.len_author)
        self.E___data = Entry(self.FRMID, font=self.f, textvariable=self.len___data)
        # Максимальное количество символов
        self.len___name.trace_variable('w', self.max_count_chars___name)
        self.len_author.trace_variable('w', self.max_count_chars_author)
        self.len___data.trace_variable('w', self.max_count_chars___data)

        self.chars_status.pack(fill=X)
        self.CHECK_1.pack(side=RIGHT)
        self.combobox.pack(side=TOP, fill=X)
        self.chars___name.pack(fill=X)
        self.CHECK_2.pack(side=RIGHT)
        self.E___name.pack(side=TOP, fill=X)
        self.chars_author.pack(fill=X)
        self.CHECK_3.pack(side=RIGHT)
        self.E_author.pack(side=TOP, fill=X)
        self.chars___data.pack(fill=X)
        self.CHECK_4.pack(side=RIGHT)
        self.E___data.pack(side=TOP, fill=X)
        self.FRMID.pack(fill=BOTH, padx=10, pady=10)
        self.E___name.focus()

        # УДЕРЖИВАЕМ НАШЕ ВСПЛЫВАЮЩЕЕ ОКНО 'ВВЕРХУ';
        self.grab_set()
        self.focus_set()

    def max_count_chars___name(self, name, index, mode):
        count = 6
        msg = self.len___name.get()
        if len(msg) > count: self.len___name.set(msg[:count])
        self.CHECK_2['text'] = '0%d/0%d' % (len(self.len___name.get()), count)

        if search(r'\d{6}', self.len___name.get()):
            print(True)
        else: print(False)

    def max_count_chars_author(self, name, index, mode):
        count = 3
        msg = self.len_author.get()
        if len(msg) > count: self.len_author.set(msg[:count])
        self.CHECK_3['text'] = '0%d/0%d' % (len(self.len_author.get()), count)

    def max_count_chars___data(self, name, index, mode):
        count = 21
        msg = self.len___data.get()
        if len(msg) > count: self.len___data.set(msg[:count])
        self.CHECK_4['text'] = '%d/%d' % (len(self.len___data.get()), count)
        if len(msg) < 10: self.CHECK_4['text'] = '0' + self.CHECK_4['text']


class AddData(PopupFrame): # ДОБАВЛЕНИЕ ДАННЫХ;
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.__NAMEBTN = 'ДОБАВИТЬ'
        self.init_add()
        self.view = appl

    def init_add(self):
        self.title(self.__NAMEBTN)
        self.geometry('%dx%d+%d+%d' % (self.w_pf, self.h_pf, self.x + (self.w - 300) / 2, self.y + self.h))

        self.combobox.configure(state=DISABLED)
        self.E___data.configure(state=DISABLED)

        BTNADD = Button(self.FRMID, text=self.__NAMEBTN, font=self.f, fg=self.c[4], bg=self.c[0],
                        activebackground=self.c[1], activeforeground=self.c[3], relief=GROOVE, overrelief=GROOVE)
        BTNADD.pack(fill=X, pady=(20, 0))
        BTNADD.bind('<Button-1>', lambda event: self.clear_entry_and_add_record())

    def clear_entry_and_add_record(self):
        self.view.add_record(self.E___name.get(), self.E_author.get())
        self.E___name.delete(0, END)
        self.E_author.delete(0, END)


class EditData(PopupFrame): # РЕДАКТИРОВАНИЕ ДАННЫХ;
    def __init__(self, x, y, w, h, val___name, val_author, val___data):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vn = val___name
        self.va = val_author
        self.vd = val___data
        self.__NAMEBTN = 'РЕДАКТИРОВАТЬ'
        self.init_add()
        self.view = appl

    def init_add(self):
        self.title(self.__NAMEBTN)
        self.geometry('%dx%d+%d+%d' % (self.w_pf, self.h_pf, self.x + (self.w - 300) / 2, self.y + self.h))

        self.combobox.configure(state=DISABLED)

        # ДОБАВЛЯЕМ ЗАПИСИ В ПОЛЯ;
        self.E___name.insert(0, self.vn)
        self.E_author.insert(0, self.va)
        self.E___data.insert(0, self.vd)
        
        # КНОПКА для РЕДАКТИРОВАНИЯ и ЗАКРЫТИЯ ОКНА;
        BTNEDI = Button(self.FRMID, text=self.__NAMEBTN, font=self.f, fg=self.c[4], bg=self.c[0], command=self.destroy,
                        activebackground=self.c[1], activeforeground=self.c[3], relief=GROOVE, overrelief=GROOVE)
        BTNEDI.pack(fill=X, pady=(20, 0))
        BTNEDI.bind('<Button-1>', lambda event: self.view.edit_record(
            self.E___name.get(), self.E_author.get(), self.E___data.get()
        ))


class SearchData(PopupFrame): # ПОИСК ДАННЫХ
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.__NAMEBTN = 'ПОИСК'
        self.init_search()
        self.view = appl

    def init_search(self):
        self.title(self.__NAMEBTN)
        self.geometry('%dx%d+%d+%d' % (self.w_pf, self.h_pf, self.x + (self.w - 300) / 2, self.y + self.h))

        self.CHECK_1.configure(state=NORMAL)
        self.CHECK_2.configure(state=NORMAL)
        self.CHECK_3.configure(state=NORMAL)
        self.CHECK_4.configure(state=NORMAL)
        self.combobox.configure(state='readonly')

        # КНОПКА для ПОИСКА и ЗАКРЫТИЯ ОКНА;
        BTN_SRC = Button(self.FRMID, text=self.__NAMEBTN, font=self.f, fg=self.c[4], bg=self.c[0], #command=self.destroy,
                         activebackground=self.c[1], activeforeground=self.c[3], relief=GROOVE, overrelief=GROOVE)
        BTN_SRC.pack(fill=X, pady=(20, 0))
        BTN_SRC.bind('<Button-1>', lambda event: self.view.search_record(
            [ self.state_1.get(),  self.state_2.get(),  self.state_3.get(),  self.state_4.get() ],
            [ self.combobox.get(), self.E___name.get(), self.E_author.get(), self.E___data.get() ]
        ))


if __name__ == '__main__':
    root = Tk()
    WIDTH  = 430
    HEIGHT = 518
    x = root.winfo_screenwidth()  / 2 - WIDTH  / 2
    y = root.winfo_screenheight() / 2 - HEIGHT / 2
    root.title('Caption')
    # root.iconbitmap('data/ai.ico')
    root.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, x, y))
    root.resizable(False, False)
    db = DataBase()
    appl = Aibolit(root, x, y, WIDTH, HEIGHT)
    appl.pack()
    root.mainloop()