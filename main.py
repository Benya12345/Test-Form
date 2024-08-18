import tkinter as tk
import sqlite3 as sql
import random

def initialize_database():
    with sql.connect('TESTS.db') as db:
        c = db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS profiles (
            name text,
            surname text,
            mark int,
            mem int
        )""")
        db.commit()

def create_test_table():
    global ID
    ID = random.randint(0, 10000)
    with sql.connect('TESTS.db') as db:
        c = db.cursor()
        c.execute(f"""CREATE TABLE IF NOT EXISTS test_{ID} (
            q text,
            a1 text,
            a2 text,
            ca int
        )""")
        db.commit()

def create_question():
    question = en1.get()
    answer1 = en2.get()
    answer2 = en3.get()
    correct_answer_index = int(en4.get())

    with sql.connect('TESTS.db') as db:
        c = db.cursor()
        c.execute(f"""INSERT INTO test_{ID} (q, a1, a2, ca) VALUES (?, ?, ?, ?)""",
                  (question, answer1, answer2, correct_answer_index))
        db.commit()

    en1.delete(0, tk.END)
    en2.delete(0, tk.END)
    en3.delete(0, tk.END)
    en4.delete(0, tk.END)

def create_test_window():
    global new_window, en1, en2, en3, en4
    create_test_table()

    new_window = tk.Toplevel(root)
    new_window.title("Конструктор")
    new_window.geometry('500x500')

    en1 = tk.Entry(new_window)
    bn4 = tk.Button(new_window, text='Зберегти', command=create_question)
    en2 = tk.Entry(new_window)
    en3 = tk.Entry(new_window)
    en4 = tk.Entry(new_window)
    ln = tk.Label(new_window,
                  text="Введіть питання в перше поле, варіанти в друге і третє поля, а номер правильної відповіді в четверте поле",
                  wraplength=500,
                  justify=tk.LEFT)
    ln2 = tk.Label(new_window, text=f"Test ID: {ID}")
    ln.pack()
    ln2.pack(pady=5)

    en1.pack(pady=5)
    en2.pack(pady=5)
    en3.pack(pady=5)
    en4.pack(pady=5)
    bn4.pack(pady=5)

    new_window.mainloop()

def save_registration():
    name = ex1.get()
    surname = ex2.get()
    ID_mem = int(ex3.get())

    with sql.connect('TESTS.db') as db:
        c = db.cursor()
        c.execute(f"""INSERT INTO profiles (name, surname, mark, mem) VALUES (?, ?, ?, ?)""",
                  (name, surname, '', ID_mem))
        db.commit()

    ex1.delete(0, tk.END)
    ex2.delete(0, tk.END)
    ex3.delete(0, tk.END)

def registration():
    global new_window2, ex1, ex2, ex3
    new_window2 = tk.Toplevel(root)
    new_window2.title("Рєстрація учасника")
    new_window2.geometry('500x500')
    name = tk.StringVar(value="Імя")
    surn = tk.StringVar(value="Призвище")
    pix = tk.StringVar(value="ID Учасника")
    ex1 = tk.Entry(new_window2, textvariable=name)
    ex1.pack()
    ex2 = tk.Entry(new_window2, textvariable=surn)
    ex2.pack()
    ex3 = tk.Entry(new_window2, textvariable=pix)
    ex3.pack()
    bx1 = tk.Button(new_window2, text = 'Зберегти', command=save_registration)
    bx1.pack()

    new_window2.mainloop()

def take_test():
    test_id = e1.get()
    participant_id = e2.get()

    with sql.connect('TESTS.db') as db:
        c = db.cursor()
        c.execute(f"SELECT q, a1, a2, ca FROM test_{test_id}")
        questions = c.fetchall()

    if not questions:
        tk.messagebox.showerror("Помилка!", "Такого ID не існує")
        return

    global current_question, score, question_window, answer_var

    current_question = 0
    score = 0
    answer_var = tk.IntVar()

    question_window = tk.Toplevel(root)
    question_window.title(f"Тест {test_id}")
    question_window.geometry('500x500')

    show_question(questions, participant_id)

def show_question(questions, participant_id):
    if current_question < len(questions):
        question, answer1, answer2, correct_answer = questions[current_question]

        for widget in question_window.winfo_children():
            widget.destroy()

        question_label = tk.Label(question_window, text=question)
        question_label.pack(pady=10)

        answer1_rb = tk.Radiobutton(question_window, text=answer1, variable=answer_var, value=1)
        answer1_rb.pack(pady=5)

        answer2_rb = tk.Radiobutton(question_window, text=answer2, variable=answer_var, value=2)
        answer2_rb.pack(pady=5)

        next_button = tk.Button(question_window, text="Наступний", command=lambda: next_question(questions, correct_answer, participant_id))
        next_button.pack(pady=10)
    else:
        finish_test(participant_id)

def next_question(questions, correct_answer, participant_id):
    global current_question, score

    if answer_var.get() == correct_answer:
        score += 1

    current_question += 1
    show_question(questions, participant_id)

def finish_test(participant_id):
    for widget in question_window.winfo_children():
        widget.destroy()

    result_label = tk.Label(question_window, text=f"Тест завершено. Твій результат: {score} з {current_question}")
    result_label.pack(pady=20)

    with sql.connect('TESTS.db') as db:
        c = db.cursor()
        c.execute("UPDATE profiles SET mark = ? WHERE mem = ?", (score, participant_id))
        db.commit()

    close_button = tk.Button(question_window, text="Закрити", command=question_window.destroy)
    close_button.pack(pady=10)

root = tk.Tk()
root.geometry('500x500')
root.title('TESTS')

initialize_database()
a = tk.StringVar(value="Тест ID")
b = tk.StringVar(value="ID Учасника")
e1 = tk.Entry(root, textvariable=a)
e1.pack(pady=10)
e2 = tk.Entry(root, textvariable=b)
e2.pack(pady=10)

b1 = tk.Button(root, text='Пройти тест', command=take_test)
b1.pack(pady=10)

b2 = tk.Button(root, text='Створити тест', command=create_test_window)
b2.pack(pady=10)

b3 = tk.Button(root, text='Заєреструвати участника', command=registration)
b3.pack(pady=10)

root.mainloop()